import os

from agent.prompt_builder import build_prompt
from agent.refusal import refusal_response

from llm.client_factory import create_generation_client

from retrieval.retriever import Retriever
from retrieval.reranker import Reranker
from retrieval.context_builder import build_context


def classify_intent(_query: str) -> str:
    return "INFORMATION"


class AgentSupervisor:

    def __init__(self):

        print("Initializing Agent Supervisor...")

        self.retriever = None
        self.tables_raw = []
        self.doc_loaded = False
        self.max_context_chunks = int(os.getenv("RAG_MAX_CONTEXT_CHUNKS", "5"))
        self.min_retriever_score = float(os.getenv("RAG_MIN_RETRIEVER_SCORE", "0.15"))

        rerank_threshold = os.getenv("RAG_MIN_RERANK_SCORE", "").strip()
        self.min_rerank_score = float(rerank_threshold) if rerank_threshold else None

        self.debug_retrieval = os.getenv("RAG_DEBUG_RETRIEVAL", "").strip().lower() in {
            "1", "true", "yes", "on"
        }

        self.reranker = Reranker()
        self.generation_client, self.generation_error = create_generation_client(task="generation")
        self.hf_client = self.generation_client

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

    def _select_grounded_matches(self, ranked_results):

        grounded_matches = []

        for result in ranked_results:
            retriever_score = result.get("score")
            rerank_score = result.get("rerank_score")

            if retriever_score is not None and retriever_score < self.min_retriever_score:
                continue

            if self.min_rerank_score is not None and rerank_score is not None and rerank_score < self.min_rerank_score:
                continue

            grounded_matches.append(result)

            if len(grounded_matches) >= self.max_context_chunks:
                break

        return grounded_matches

    def _log_retrieval(self, candidates, ranked_results, grounded_results):

        if not self.debug_retrieval:
            return

        print(
            "RAG retrieval debug:",
            {
                "candidate_count": len(candidates),
                "ranked_count": len(ranked_results),
                "grounded_count": len(grounded_results),
                "min_retriever_score": self.min_retriever_score,
                "min_rerank_score": self.min_rerank_score,
                "max_context_chunks": self.max_context_chunks,
                "top_candidates": [
                    {
                        "chunk_id": item.get("chunk_id"),
                        "score": round(float(item.get("score", 0.0)), 4),
                        "rerank_score": round(float(item.get("rerank_score", 0.0)), 4),
                        "pages": item.get("pages", []),
                        "section": item.get("section", ""),
                    }
                    for item in ranked_results[: min(5, len(ranked_results))]
                ],
            },
        )

    def handle(self, query: str):

        intent = classify_intent(query)

        if intent == "ACTION":

            try:
                raw_output = self.generation_client.generate(query)
            except self.generation_error:
                return {
                    "type": "action",
                    "answer": "Model temporarily unavailable."
                }

            import json

            try:
                extracted = json.loads(raw_output)

                if not isinstance(extracted, dict):
                    raise ValueError("Output must be a dictionary")

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

        grounded_results = self._select_grounded_matches(ranked_results)
        self._log_retrieval(candidates, ranked_results, grounded_results)

        if not grounded_results:
            return {
                "type": "information",
                "answer": refusal_response()
            }

        context_payload = build_context(grounded_results)
        context_items = context_payload.get("context", [])

        if not context_items:
            return {
                "type": "information",
                "answer": refusal_response()
            }

        top_matches = context_items[:self.max_context_chunks]

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
            answer = self.generation_client.generate(prompt)
        except self.generation_error:
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
