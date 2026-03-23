import json


import re

def generate_table_summary(table):
    """
    Programmatic summary extracting the first few cells or words.
    Ensures unique embeddings for semantic retrieval.
    """
    table_type = table.get("table_type")
    
    if table_type == "structured":
        html = table.get("table_html", "")
        # Extract text from th and td tags
        cells = re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', html, re.IGNORECASE | re.DOTALL)
        # Strip internal html tags
        cells = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
        cells = [c for c in cells if c]
        
        if cells:
            preview = ", ".join(cells[:10])
            return f"Structured table containing columns/data: [{preview} ...]"
        return "Structured table with rows and columns."

    # For unstructured, use the beginning of raw_text
    raw = table.get("raw_text", "").strip()
    if raw:
        preview = " ".join(raw.split()[:20])
        return f"Table containing data: [{preview} ...]"

    return "Unstructured table containing numeric or textual data."


def process_tables(input_path, raw_output_path, index_output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        tables = json.load(f)

    tables_raw = []
    tables_index = []

    for table in tables:
        base = {
            "id": table.get("id"),
            "page": table.get("page"),
            "order": table.get("order"),
            "table_type": table.get("table_type")
        }

        # -------------------------------
        # STRUCTURED TABLE (HTML)
        # -------------------------------
        if table.get("table_type") == "structured":
            tables_raw.append({
                **base,
                "table_html": table.get("table_html", "")
            })

        # -------------------------------
        # UNSTRUCTURED TABLE (FALLBACK)
        # -------------------------------
        else:
            tables_raw.append({
                **base,
                "raw_text": table.get("raw_text", "")
            })

        # -------------------------------
        # INDEX ENTRY (RETRIEVAL ONLY)
        # -------------------------------
        tables_index.append({
            "id": table.get("id"),
            "page": table.get("page"),
            "summary": generate_table_summary(table)
        })

    with open(raw_output_path, "w", encoding="utf-8") as f:
        json.dump(tables_raw, f, indent=2, ensure_ascii=False)

    with open(index_output_path, "w", encoding="utf-8") as f:
        json.dump(tables_index, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    process_tables(
        input_path="data/processed/table_elements.json",
        raw_output_path="data/processed/tables_raw.json",
        index_output_path="data/processed/tables_index.json"
    )
