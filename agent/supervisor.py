import json
import logging
from agent.preprocess import normalize_query
from agent.planner import generate_plan
from agent.action_builder import build_action
from agent.schemas import PLANNER_CONFIDENCE_THRESHOLD
from agent.refusal import refusal_response

# RAG untouched
from retrieval.retriever import Retriever
from retrieval.reranker import Reranker
from retrieval.context_builder import build_context
from agent.prompt_builder import build_prompt
from llm.ollama_client import call_ollama

logging.basicConfig(
    filename="agent_audit.log",
    level=logging.INFO,
    format="%(asctime)s | %(message)s"
)

class AgentSupervisor:
    def __init__(self):
        self.retriever = Retriever(
            index_path="data/processed/chunks.faiss",
            meta_path="data/processed/chunks_meta.json",
            initial_top_k=25
        )
        self.reranker = Reranker()

    def handle(self, raw_query: str):
        query = normalize_query(raw_query)
        plan = generate_plan(query)

        logging.info(f"QUERY: {raw_query} | PLAN: {plan}")

        actions_allowed = plan["confidence"] >= PLANNER_CONFIDENCE_THRESHOLD
        intent = plan["intent"]

        if intent == "INFORMATION":
            return self._rag(query)

        if intent == "ACTION":
            if not actions_allowed:
                return self._rag(query)
            return build_action(plan, raw_query)

        if intent == "INFORMATION_AND_ACTION":
            answer = self._rag(query)
            if not actions_allowed:
                return answer
            return {
                "answer": answer,
                "action": build_action(plan, raw_query)
            }

        return refusal_response("Unhandled intent")

    def _rag(self, query: str):
        candidates = self.retriever.retrieve(query)
        ranked = self.reranker.rerank(query, candidates, top_k=5)

        if not ranked:
            return refusal_response("Information not found")

        ctx = build_context(ranked)["context"][0]
        prompt = build_prompt(
            question=query,
            section_text=ctx["text"],
            tables=[],
            page=ctx["pages"][0] if ctx["pages"] else "Unknown"
        )
        return {
            "answer": call_ollama(prompt),
            "page": ctx["pages"][0] if ctx["pages"] else "Unknown"
        }
