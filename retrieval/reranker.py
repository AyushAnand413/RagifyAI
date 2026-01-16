import torch
from sentence_transformers import CrossEncoder

class Reranker:
    def __init__(self, model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Recommended defaults:
        - CPU friendly
        - Strong reranking performance
        - Fast enough for local demos
        """
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading reranker: {model_name} on {device}")
        self.model = CrossEncoder(model_name, device=device)

    def rerank(self, query: str, results: list, top_k: int = 10):
        if not results:
            return []

        # Build (query, document) pairs
        pairs = []
        for r in results:
            context = f"{r.get('section', '')}: {r.get('chunk_text', '')}"
            pairs.append([query, context])

        scores = self.model.predict(pairs)

        for r, s in zip(results, scores):
            r["rerank_score"] = float(s)

        # Sort by cross-encoder score (descending)
        results.sort(key=lambda x: x["rerank_score"], reverse=True)

        return results[:top_k]


# Optional helper for backward compatibility
def filter_results_professional(query, results, reranker, top_k=5):
    return reranker.rerank(query, results, top_k=top_k)
