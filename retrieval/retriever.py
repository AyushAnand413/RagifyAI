import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

MODEL_NAME = "BAAI/bge-base-en"
RRF_K = 60


def _tokenize(text: str) -> list:
    return text.lower().split()


def _reciprocal_rank_fusion(ranked_lists: list, k: int = RRF_K) -> dict:
    """Merge multiple ranked lists into {chunk_id: rrf_score}."""
    scores = {}
    for ranked in ranked_lists:
        for rank, item in enumerate(ranked):
            cid = item["chunk_id"]
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank + 1)
    return scores


class Retriever:
    def __init__(
        self,
        index_path=None,
        meta_path=None,
        initial_top_k=25,
        index_object=None,
        metadata_object=None,
    ):
        """
        initial_top_k:
        Fetch a broad candidate set so the reranker
        can make an accurate final decision.

        Supports two modes:
        1) Disk mode: index_path + meta_path
        2) In-memory mode: index_object + metadata_object
        """
        self.model = SentenceTransformer(MODEL_NAME)

        in_memory_mode = index_object is not None or metadata_object is not None
        disk_mode = index_path is not None or meta_path is not None

        if in_memory_mode and disk_mode:
            raise ValueError("Provide either disk paths or in-memory objects, not both.")

        if in_memory_mode:
            if index_object is None or metadata_object is None:
                raise ValueError("Both index_object and metadata_object are required for in-memory mode.")
            self.index = index_object
            self.meta = metadata_object
        else:
            if index_path is None or meta_path is None:
                raise ValueError("Both index_path and meta_path are required for disk mode.")
            self.index = faiss.read_index(index_path)
            with open(meta_path, "r", encoding="utf-8") as f:
                self.meta = json.load(f)

        self.initial_top_k = initial_top_k
        self._build_bm25()

    def _build_bm25(self):
        corpus = [_tokenize(m.get("chunk_text", "")) for m in self.meta]
        self.bm25 = BM25Okapi(corpus)

    def _dense_retrieve(self, query: str) -> list:
        query_vec = self.model.encode([query], normalize_embeddings=True)
        scores, indices = self.index.search(query_vec.astype(np.float32), self.initial_top_k)
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            meta = self.meta[idx]
            results.append({
                "score": float(score),
                "chunk_id": meta["chunk_id"],
                "section": meta.get("section", ""),
                "pages": meta.get("pages", []),
                "tables": meta.get("tables", []),
                "images": meta.get("images", []),
                "chunk_text": meta.get("chunk_text", ""),
            })
        return results

    def _bm25_retrieve(self, query: str) -> list:
        tokens = _tokenize(query)
        bm25_scores = self.bm25.get_scores(tokens)
        top_indices = np.argsort(bm25_scores)[::-1][: self.initial_top_k]
        results = []
        for idx in top_indices:
            meta = self.meta[idx]
            results.append({
                "score": float(bm25_scores[idx]),
                "chunk_id": meta["chunk_id"],
                "section": meta.get("section", ""),
                "pages": meta.get("pages", []),
                "tables": meta.get("tables", []),
                "images": meta.get("images", []),
                "chunk_text": meta.get("chunk_text", ""),
            })
        return results

    def retrieve(self, query: str) -> list:
        dense_results = self._dense_retrieve(query)
        bm25_results = self._bm25_retrieve(query)

        rrf_scores = _reciprocal_rank_fusion([dense_results, bm25_results])

        # Build lookup from chunk_id → full result dict (dense takes precedence for metadata)
        chunk_map = {r["chunk_id"]: r for r in bm25_results}
        chunk_map.update({r["chunk_id"]: r for r in dense_results})

        merged = []
        for chunk_id, rrf_score in sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True):
            entry = dict(chunk_map[chunk_id])
            entry["score"] = rrf_score
            merged.append(entry)

        return merged[: self.initial_top_k]
