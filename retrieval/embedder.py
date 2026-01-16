import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "BAAI/bge-base-en"

def build_faiss_index(chunks_path, index_path, meta_path):
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    model = SentenceTransformer(MODEL_NAME)

    texts = []
    metadata = []

    for chunk in chunks:
        chunk_text = f"{chunk['section']}\n{chunk['text']}"

        texts.append(chunk_text)

        metadata.append({
            "chunk_id": chunk["chunk_id"],
            "section": chunk["section"],
            "pages": chunk["pages"],
            "tables": chunk["tables"],
            "images": chunk["images"],
            "chunk_text": chunk_text
        })

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # cosine similarity
    index.add(embeddings.astype(np.float32))

    faiss.write_index(index, index_path)

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    build_faiss_index(
        chunks_path="data/processed/chunks.json",
        index_path="data/processed/chunks.faiss",
        meta_path="data/processed/chunks_meta.json"
    )
