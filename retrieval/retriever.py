import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "BAAI/bge-base-en"

class Retriever:
    def __init__(self, index_path, meta_path, initial_top_k=25):
        """
        initial_top_k:
        Fetch a broad candidate set so the reranker
        can make an accurate final decision.
        """
        self.model = SentenceTransformer(MODEL_NAME)
        self.index = faiss.read_index(index_path)

        with open(meta_path, "r", encoding="utf-8") as f:
            self.meta = json.load(f)

        self.initial_top_k = initial_top_k

    def retrieve(self, query: str):
        query_vec = self.model.encode(
            [query],
            normalize_embeddings=True
        )

        scores, indices = self.index.search(
            query_vec.astype(np.float32),
            self.initial_top_k
        )

        results = []

        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue

            meta = self.meta[idx]

            results.append({
                "score": float(score),                 # cosine similarity
                "chunk_id": meta["chunk_id"],
                "section": meta.get("section", ""),
                "pages": meta.get("pages", []),
                "tables": meta.get("tables", []),
                "images": meta.get("images", []),
                # 🔑 canonical text field
                "chunk_text": meta.get("chunk_text", "")
            })

        return results
