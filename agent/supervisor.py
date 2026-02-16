import os

from agent.prompt_builder import build_prompt
from agent.refusal import refusal_response

from llm.hf_inference_client import HFInferenceClient, HFGenerationError

from retrieval.retriever import Retriever
from retrieval.reranker import Reranker
from retrieval.context_builder import build_context


# =====================================================
# TEST COMPATIBILITY STUB
# =====================================================
# Required because pytest expects this symbol.
# We force INFORMATION always (pure RAG mode).
# =====================================================

def classify_intent(_query: str) -> str:
    return "INFORMATION"



class AgentSupervisor:

    def __init__(self):

        print("🤖 Initializing Agent Supervisor...")

        self.retriever = None
        self.tables_raw = []
        self.doc_loaded = False

        self.reranker = Reranker()

        self.hf_client = HFInferenceClient(
            api_token=os.getenv("HF_TOKEN", ""),
            generation_model=os.getenv(
                "HF_GENERATION_MODEL",
                "meta-llama/Llama-3.2-1B-Instruct:novita"
            ),
            timeout=120,
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


    def _load_tables(self, table_ids):

        if not table_ids:
            return []

        loaded_tables = []

        for table in self.tables_raw:

            if table.get("id") not in table_ids:
                continue

            if table.get("table_type") == "structured":

                html = table.get("table_html")

                if html:
                    loaded_tables.append(html)

            elif table.get("raw_text"):

                loaded_tables.append(table.get("raw_text"))

        return loaded_tables


    # =====================================================
    # PURE RAG HANDLER
    # =====================================================

    def handle(self, query: str):

        # =====================================================
        # INTENT CHECK (for pytest compatibility)
        # =====================================================

        intent = classify_intent(query)


        # =====================================================
        # ACTION FLOW (used only if explicitly requested)
        # =====================================================

        if intent == "ACTION":

            try:

                raw_output = self.hf_client.generate(query)

            except HFGenerationError:

                return {
                    "type": "action",
                    "answer": "Model temporarily unavailable."
                }

            import json

            try:

                extracted = json.loads(raw_output)

            except Exception:

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


        # =====================================================
        # INFORMATION FLOW (PURE RAG)
        # =====================================================

        if not self.has_active_document():

            return {
                "type": "information",
                "answer": "Please upload a PDF first."
            }


        candidates = self.retriever.retrieve(query)

        if not candidates:

            return {
                "type": "information",
                "answer": refusal_response()
            }


        ranked_results = self.reranker.rerank(
            query,
            candidates,
            top_k=7
        )


        if not ranked_results:

            return {
                "type": "information",
                "answer": refusal_response()
            }


        context_payload = build_context(ranked_results)

        context_items = context_payload.get("context", [])

        if not context_items:

            return {
                "type": "information",
                "answer": refusal_response()
            }


        top_matches = context_items[:2]


        context_parts = []

        for chunk in top_matches:

            pages = chunk.get("pages", [])

            page_str = ", ".join(str(p) for p in pages) if pages else "Unknown"

            text = chunk.get("text", "").strip()

            if text:

                context_parts.append(
                    f"[Source: Page {page_str}]\n{text}"
                )


        merged_text = "\n\n---\n\n".join(context_parts)


        table_ids = set()

        for chunk in top_matches:

            table_ids.update(chunk.get("tables", []))


        raw_tables = self._load_tables(table_ids)


        prompt = build_prompt(

            question=query,

            section_text=merged_text,

            tables=raw_tables,

            page="Unknown",

        )


        try:

            answer = self.hf_client.generate(prompt)

        except HFGenerationError:

            return {
                "type": "information",
                "answer": "Model temporarily unavailable."
            }


        if not answer:

            return {
                "type": "information",
                "answer": refusal_response()
            }


        if answer.strip() == "Information not found in the document.":

            return {
                "type": "information",
                "answer": refusal_response()
            }


        return {

            "type": "information",

            "answer": answer.strip()

        }

