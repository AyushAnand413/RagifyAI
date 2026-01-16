from unstructured.partition.pdf import partition_pdf
import json


# -------------------------------
# NORMALIZE ELEMENT TYPE
# -------------------------------

def normalize_type(el):
    name = type(el).__name__

    if name == "Title":
        return "Title"
    if name in ["NarrativeText", "Text", "CompositeElement"]:
        return "NarrativeText"
    if name == "Table":
        return "Table"
    if name in ["Image", "Figure"]:
        return "Image"

    return "Unknown"


# -------------------------------
# EXTRACT TABLE PAYLOAD (CRITICAL)
# -------------------------------

def extract_table_payload(el):
    """
    Preserve table structure if available.
    NEVER rely on flattened text for tables.
    """

    html = None

    if el.metadata:
        html = (
            getattr(el.metadata, "text_as_html", None)
            or getattr(el.metadata, "table_as_html", None)
        )

    if html:
        return {
            "table_type": "structured",
            "table_html": html
        }
    else:
        return {
            "table_type": "unstructured",
            "raw_text": el.text if hasattr(el, "text") else None
        }


# -------------------------------
# MAIN PDF PARSER
# -------------------------------

def parse_pdf(pdf_path: str, output_path: str):
    elements = partition_pdf(
        filename=pdf_path,
        infer_table_structure=True,
        extract_images_in_pdf=True,
        include_page_breaks=False
    )

    parsed_elements = []
    order = 0

    for el in elements:
        # Skip empty junk text
        if hasattr(el, "text") and el.text and el.text.strip() == "":
            continue

        order += 1

        page = None
        if el.metadata and hasattr(el.metadata, "page_number"):
            page = el.metadata.page_number

        element_type = normalize_type(el)

        metadata = {
            "confidence": None,
            "source": "unstructured",
            "raw_type": type(el).__name__
        }

        # -------------------------------
        # IMAGE ELEMENT
        # -------------------------------
        if element_type == "Image":
            if el.metadata and hasattr(el.metadata, "image_path"):
                metadata["image_path"] = el.metadata.image_path

            parsed_elements.append({
                "id": f"el_{order:06d}",
                "type": "Image",
                "page": page,
                "order": order,
                "metadata": metadata
            })
            continue

        # -------------------------------
        # TABLE ELEMENT (STRUCTURE SAFE)
        # -------------------------------
        if element_type == "Table":
            table_payload = extract_table_payload(el)

            parsed_elements.append({
                "id": f"el_{order:06d}",
                "type": "Table",
                "page": page,
                "order": order,
                "metadata": metadata,
                **table_payload
            })
            continue

        # -------------------------------
        # TEXT / TITLE ELEMENT
        # -------------------------------
        parsed_elements.append({
            "id": f"el_{order:06d}",
            "type": element_type,
            "text": el.text if hasattr(el, "text") else None,
            "page": page,
            "order": order,
            "metadata": metadata
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(parsed_elements, f, indent=2, ensure_ascii=False)


# -------------------------------
# CLI ENTRYPOINT
# -------------------------------

if __name__ == "__main__":
    parse_pdf(
        pdf_path="data/raw/hcltech_report.pdf",
        output_path="data/processed/parsed_elements.json"
    )
