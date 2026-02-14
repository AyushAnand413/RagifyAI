import json
import os
import tempfile

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from ingestion.pdf_parser import parse_pdf
from ingestion.router import route_elements
from ingestion.table_processor import process_tables
from ingestion.chunker import build_chunks

MODEL_NAME = "BAAI/bge-base-en"


def ingest_pdf_to_runtime(pdf_path: str) -> dict:
    with tempfile.TemporaryDirectory(prefix="runtime_ingestion_") as work_dir:
        parsed_path = os.path.join(work_dir, "parsed_elements.json")
        text_elements_path = os.path.join(work_dir, "text_elements.json")
        table_elements_path = os.path.join(work_dir, "table_elements.json")
        tables_raw_path = os.path.join(work_dir, "tables_raw.json")
        tables_index_path = os.path.join(work_dir, "tables_index.json")
        chunks_path = os.path.join(work_dir, "chunks.json")
        missing_images_path = os.path.join(work_dir, "image_semantics.json")

        parse_pdf(pdf_path=pdf_path, output_path=parsed_path)
        route_elements(input_path=parsed_path, output_dir=work_dir)

        process_tables(
            input_path=table_elements_path,
            raw_output_path=tables_raw_path,
            index_output_path=tables_index_path,
        )

        build_chunks(
            text_path=text_elements_path,
            tables_index_path=tables_index_path,
            images_path=missing_images_path,
            output_path=chunks_path,
        )

        with open(chunks_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        with open(tables_raw_path, "r", encoding="utf-8") as f:
            tables_raw = json.load(f)

        texts = []
        metadata = []

        for chunk in chunks:
            chunk_text = f"{chunk['section']}\n{chunk['text']}"
            texts.append(chunk_text)
            metadata.append(
                {
                    "chunk_id": chunk["chunk_id"],
                    "section": chunk["section"],
                    "pages": chunk["pages"],
                    "tables": chunk["tables"],
                    "images": chunk["images"],
                    "chunk_text": chunk_text,
                }
            )

        if not texts:
            raise ValueError("No text chunks extracted from uploaded PDF.")

        model = SentenceTransformer(MODEL_NAME)
        embeddings = model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        dim = embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(np.asarray(embeddings, dtype=np.float32))

        return {
            "index": index,
            "metadata": metadata,
            "tables": tables_raw,
        }
