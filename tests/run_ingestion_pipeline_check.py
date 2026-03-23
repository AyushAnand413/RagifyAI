import json
import os
import shutil
import sys
import uuid

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from ingestion.chunker import build_chunks
from ingestion.router import route_elements
from ingestion.table_processor import process_tables


def _write_json(path, payload):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def _load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def run_check():
    sample_elements = [
        {
            "id": "el_000001",
            "type": "Title",
            "text": "Quarterly Highlights",
            "page": 1,
            "order": 1,
            "metadata": {"source": "test", "raw_type": "Title"},
        },
        {
            "id": "el_000002",
            "type": "NarrativeText",
            "text": "Revenue grew 15 percent year over year in the first quarter.",
            "page": 1,
            "order": 2,
            "metadata": {"source": "test", "raw_type": "NarrativeText"},
        },
        {
            "id": "el_000003",
            "type": "ListItem",
            "text": "Operating margin improved to 22 percent.",
            "page": 1,
            "order": 3,
            "metadata": {"source": "test", "raw_type": "ListItem"},
        },
        {
            "id": "el_000004",
            "type": "Table",
            "text": "Quarter Revenue Margin",
            "page": 1,
            "order": 4,
            "table_type": "structured",
            "table_html": (
                "<table><tr><th>Quarter</th><th>Revenue</th><th>Margin</th></tr>"
                "<tr><td>Q1</td><td>120</td><td>22%</td></tr></table>"
            ),
            "metadata": {"source": "test", "raw_type": "Table"},
        },
        {
            "id": "el_000005",
            "type": "Footer",
            "text": "Confidential",
            "page": 1,
            "order": 5,
            "metadata": {"source": "test", "raw_type": "Footer"},
        },
    ]

    scratch_root = os.path.join(ROOT_DIR, ".tmp_ingestion_checks")
    os.makedirs(scratch_root, exist_ok=True)
    work_dir = os.path.join(scratch_root, f"ingestion_check_{uuid.uuid4().hex[:8]}")
    os.makedirs(work_dir, exist_ok=False)

    try:
        parsed_path = os.path.join(work_dir, "parsed_elements.json")
        tables_raw_path = os.path.join(work_dir, "tables_raw.json")
        tables_index_path = os.path.join(work_dir, "tables_index.json")
        image_semantics_path = os.path.join(work_dir, "image_semantics.json")
        chunks_path = os.path.join(work_dir, "chunks.json")

        _write_json(parsed_path, sample_elements)
        route_elements(parsed_path, work_dir)

        text_elements = _load_json(os.path.join(work_dir, "text_elements.json"))
        table_elements = _load_json(os.path.join(work_dir, "table_elements.json"))
        image_elements = _load_json(os.path.join(work_dir, "image_elements.json"))
        unknown_elements = _load_json(os.path.join(work_dir, "unknown_elements.json"))

        assert len(text_elements) == 3, "Expected title/text/list items to be routed as text."
        assert len(table_elements) == 1, "Expected one table element."
        assert len(image_elements) == 0, "Image extraction is intentionally disabled."
        assert len(unknown_elements) == 1, "Expected footer to be routed as unknown."

        process_tables(
            input_path=os.path.join(work_dir, "table_elements.json"),
            raw_output_path=tables_raw_path,
            index_output_path=tables_index_path,
        )

        tables_raw = _load_json(tables_raw_path)
        tables_index = _load_json(tables_index_path)

        assert tables_raw[0]["table_type"] == "structured", "Structured table contract broken."
        assert "table_html" in tables_raw[0], "Structured table HTML missing."
        assert tables_index[0]["summary"].startswith("Structured table"), "Table summary was not generated."

        _write_json(image_semantics_path, [])

        build_chunks(
            text_path=os.path.join(work_dir, "text_elements.json"),
            tables_index_path=tables_index_path,
            images_path=image_semantics_path,
            output_path=chunks_path,
        )

        chunks = _load_json(chunks_path)

        assert chunks, "Chunk builder produced no chunks."
        assert chunks[0]["section"] == "Quarterly Highlights", "Title routing into section failed."
        assert "Revenue grew 15 percent" in chunks[0]["text"], "Narrative text missing from chunk."
        assert tables_index[0]["id"] in chunks[0]["tables"], "Page-level table attachment failed."
        assert chunks[0]["images"] == [], "Images should stay empty when OCR/image pipeline is disabled."

        print("PASS: ingestion lightweight pipeline contract is healthy.")
        print(f"Workspace: {work_dir}")
        print(f"Chunks created: {len(chunks)}")
        print(f"Tables indexed: {len(tables_index)}")
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


if __name__ == "__main__":
    try:
        run_check()
    except AssertionError as exc:
        print(f"FAIL: {exc}")
        sys.exit(1)
    except Exception as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)
