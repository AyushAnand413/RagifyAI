import json
import os

from click import prompt

from agent.intent_classifier import classify_intent
from agent.prompt_builder import build_prompt, build_action_prompt
from agent.refusal import refusal_response
from llm.hf_inference_client import HFInferenceClient, HFGenerationError

from retrieval.retriever import Retriever
from retrieval.reranker import Reranker
from retrieval.context_builder import build_context


class AgentSupervisor:
    def __init__(self):
        print("🤖 Initializing Agent Supervisor...")

        self.retriever = None
        self.tables_raw = []
        self.doc_loaded = False

        self.reranker = Reranker()
        self.hf_client = HFInferenceClient(
            api_token=os.getenv("HF_TOKEN", ""),
            generation_model=os.getenv("HF_GENERATION_MODEL", "meta-llama/Llama-3.2-3B-Instruct:novita"),
            timeout=90
        )

    def set_active_document(self, index, metadata, tables_raw):
        self.retriever = Retriever(
            index_object=index,
            metadata_object=metadata,
            initial_top_k=25
        )
        self.tables_raw = tables_raw or []
        self.doc_loaded = True

    def has_active_document(self):
        return self.doc_loaded and self.retriever is not None

    # ---------------------------
    # Table Loader
    # ---------------------------
    def _load_tables(self, table_ids):
        loaded_tables = []

        for t in self.tables_raw:
            if t.get("id") not in table_ids:
                continue

            if t.get("table_type") == "structured" and "table_html" in t:
                loaded_tables.append(t["table_html"])
            elif "raw_text" in t:
                loaded_tables.append(t["raw_text"])

        return loaded_tables

    # ---------------------------
    # MAIN HANDLER
    # ---------------------------
    def handle(self, query: str):
        intent = classify_intent(query)

        # ==================================================
        # ACTION PATH - IT SERVICE DESK
        # ==================================================
        if intent == "ACTION":
            prompt = build_action_prompt(query)
            try:
                raw_output = self.hf_client.generate(prompt)
            except HFGenerationError:
                return {
                    "type": "action",
                    "answer": "Model temporarily unavailable. Please try again."
                }

            try:
                extracted = json.loads(raw_output)
            except json.JSONDecodeError:
                extracted = {
                    "department": "IT",
                    "issue_summary": query,
                    "priority": "Medium"
                }

            return {
                "type": "action",
                "action": "create_ticket",
                "department": extracted.get("department", "IT"),
                "description": extracted.get("issue_summary", query),
                "priority": extracted.get("priority", "Medium")
            }

        # ==================================================
        # INFORMATION PATH - RAG
        # ==================================================
        if not self.has_active_document():
            return {
                "type": "information",
                "answer": "Please upload a PDF first."
            }

        candidates = self.retriever.retrieve(query)
        ranked_results = self.reranker.rerank(query, candidates, top_k=7)

        if not ranked_results:
            return {
                "type": "information",
                "answer": refusal_response()
            }

        context_payload = build_context(ranked_results)
        top_matches = context_payload["context"][:2]

        # Inject page numbers directly into the text
        context_parts = []
        for c in top_matches:
            pages = c.get("pages", [])
            page_str = ", ".join(str(p) for p in pages) if pages else "Unknown"
            chunk_text = f"[Source: Page {page_str}]\n{c['text']}"
            context_parts.append(chunk_text)

        merged_text = "\n\n---\n\n".join(context_parts)

        # Collect tables
        table_ids = set()
        for c in top_matches:
            table_ids.update(c.get("tables", []))

        raw_tables = self._load_tables(table_ids)

        prompt = build_prompt(
            question=query,
            section_text=merged_text,
            tables=raw_tables,
            page="Unknown"  # kept for signature compatibility
        )

        try:
            answer = self.hf_client.generate(prompt)
        except HFGenerationError:
            return {
                "type": "information",
                "answer": "Model temporarily unavailable. Please try again."
            }

        if answer.strip() == "Information not found in the document.":
            return {
                "type": "information",
                "answer": refusal_response()
            }

        return {
            "type": "information",
            "answer": answer
        }
