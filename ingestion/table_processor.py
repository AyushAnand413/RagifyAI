import json


def generate_table_summary(table):
    """
    VERY conservative summary.
    No numbers. No inference.
    Used only for retrieval reference.
    """
    if table.get("table_type") == "structured":
        return "Structured table with rows and columns."

    raw = table.get("raw_text", "")
    text_lower = raw.lower()

    if "revenue" in text_lower:
        return "Table containing revenue-related data."
    if "profit" in text_lower:
        return "Table containing profit-related data."
    if "employee" in text_lower:
        return "Table containing employee-related data."

    return "Unstructured table containing numeric or textual data."


def process_tables(input_path, raw_output_path, index_output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        tables = json.load(f)

    tables_raw = []
    tables_index = []

    for table in tables:
        base = {
            "id": table["id"],
            "page": table["page"],
            "order": table["order"],
            "table_type": table["table_type"]
        }

        # -------------------------------
        # STRUCTURED TABLE (HTML)
        # -------------------------------
        if table["table_type"] == "structured":
            tables_raw.append({
                **base,
                "table_html": table["table_html"]
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
            "id": table["id"],
            "page": table["page"],
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
