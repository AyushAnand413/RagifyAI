import json

# Ensure these modules exist in your project structure
from agent.intent_classifier import classify_intent
from agent.prompt_builder import build_prompt
from agent.refusal import refusal_response
from llm.ollama_client import call_ollama

# Updated Imports for Professional RAG
from retrieval.retriever import Retriever
from retrieval.reranker import Reranker
from retrieval.context_builder import build_context

class AgentSupervisor:
    def __init__(self):
        print("🤖 Initializing Agent Supervisor...")
        
        # 1. Initialize Fast Retriever (High Recall)
        # We fetch 25 candidates to ensure we don't miss the answer
        self.retriever = Retriever(
            index_path="data/processed/chunks.faiss",
            meta_path="data/processed/chunks_meta.json",
            initial_top_k=25
        )

        # 2. Initialize Accurate Reranker (High Precision)
        # This sorts the Top 25 to find the true Top 5
        self.reranker = Reranker()

        # 3. Load Raw Tables (Legacy support for your specific table lookup)
        # Ensure this file exists, otherwise wrap in try-except
        try:
            with open("data/processed/tables_raw.json", "r", encoding="utf-8") as f:
                self.tables_raw = json.load(f)
        except FileNotFoundError:
            print("⚠️ Warning: tables_raw.json not found. Table lookups will be empty.")
            self.tables_raw = []

    def _load_tables(self, table_ids):
        """
        Load tables safely.
        Supports both structured (HTML) and unstructured tables.
        """
        loaded_tables = []

        for t in self.tables_raw:
            if t["id"] not in table_ids:
                continue

            # Structured table → HTML
            if t.get("table_type") == "structured" and "table_html" in t:
                loaded_tables.append(
                    f"[STRUCTURED TABLE]\n{t['table_html']}"
                )

            # Unstructured fallback → raw text
            elif "raw_text" in t:
                loaded_tables.append(
                    f"[UNSTRUCTURED TABLE]\n{t['raw_text']}"
                )

        return loaded_tables


    def handle(self, query: str):
        # 1. Classify Intent
        intent = classify_intent(query)

        # ---------------------------
        # ACTION PATH (Mock)
        # ---------------------------
        if intent == "ACTION":
            return {
                "action": "create_ticket",
                "department": "IT",
                "priority": "High",
                "description": query
            }

        # ---------------------------
        # RAG INFORMATION PATH
        # ---------------------------
        
        # Step A: Broad Retrieval (Get 25 candidates)
        candidates = self.retriever.retrieve(query)
        
        # Step B: Precision Reranking (Get top 5 best matches)
        ranked_results = self.reranker.rerank(query, candidates, top_k=5)

        # Guard clause: If nothing is relevant
        if not ranked_results:
            return refusal_response()

        # Step C: Build Clean Context
        context_payload = build_context(ranked_results)
        
        # Select the absolute best match for the answer generation
        # (You can expand this to use top 3, but prompt_builder currently expects one section)
        top_match = context_payload["context"][0]

        # Fetch full table content if the chunk references any tables
        raw_tables = self._load_tables(top_match.get("tables", []))

        # Step D: Construct Prompt
        prompt = build_prompt(
            question=query,
            section_text=top_match["text"],
            tables=raw_tables,
            page=top_match["pages"][0] if top_match["pages"] else "Unknown"
        )

        # Step E: LLM Generation
        answer = call_ollama(prompt)

        return {
            "answer": answer,
            "page": top_match["pages"][0] if top_match["pages"] else "Unknown",
            "context_score": ranked_results[0].get("rerank_score", 0)
        }