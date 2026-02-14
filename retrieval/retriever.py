import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "BAAI/bge-base-en"


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
                # canonical text field
                "chunk_text": meta.get("chunk_text", "")
            })

        return results
