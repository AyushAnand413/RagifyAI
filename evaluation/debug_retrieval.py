import os
import sys
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# ---------------- CONFIG (MATCH INGESTION EXACTLY) ----------------
MODEL_NAME = "BAAI/bge-base-en"

FAISS_INDEX_PATH = "data/processed/chunks.faiss"
METADATA_PATH = "data/processed/chunks_meta.json"

TOP_K = 5
# ------------------------------------------------------------------


def debug_retrieval(query: str):
    print("\n==============================")
    print(f"🔎 QUERY: {query}")
    print("==============================\n")

    # 1️⃣ Load FAISS index
    index = faiss.read_index(FAISS_INDEX_PATH)

    # 2️⃣ Load metadata
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    # 3️⃣ Load SAME embedding model used at ingestion
    model = SentenceTransformer(MODEL_NAME)

    # 4️⃣ Embed query
    query_embedding = model.encode(
        [query],
        normalize_embeddings=True
    ).astype(np.float32)

    # 5️⃣ Search
    scores, indices = index.search(query_embedding, TOP_K)

    # 6️⃣ Display results
    for rank, (idx, score) in enumerate(zip(indices[0], scores[0]), start=1):
        chunk = metadata[idx]

        print(f"--- Rank {rank} ---")
        print(f"Score   : {float(score):.4f}")
        print(f"Section : {chunk.get('section')}")
        print(f"Pages   : {chunk.get('pages')}")
        print("\nChunk Text:")
        print(chunk.get("chunk_text")[:1200])
        print("\n------------------------------\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python evaluation/debug_retrieval.py \"your question here\"")
        sys.exit(1)

    debug_retrieval(sys.argv[1])
    