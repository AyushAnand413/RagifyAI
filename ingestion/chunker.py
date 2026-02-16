import json
import os

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_chunks(
    text_path,
    tables_index_path,
    images_path,
    output_path
):
    text_elements = load_json(text_path)
    tables_index = load_json(tables_index_path)
    images = load_json(images_path) if os.path.exists(images_path) else []

    chunks = []

    current_section = None
    current_text = []
    current_pages = set()

    chunk_id = 0

    def flush_chunk():
        nonlocal chunk_id, current_section, current_text, current_pages

        if not current_section or not current_text:
            return

        pages = sorted(list(current_pages))

        attached_tables = [
            t["id"]
            for t in tables_index
            if t["page"] in pages
        ]

        attached_images = [
            {
                "page": img["page"],
                "caption": img["caption"]
            }
            for img in images
            if img["page"] in pages
        ]

        chunk_id += 1

        chunks.append({
            "chunk_id": f"chunk_{chunk_id:03d}",
            "section": current_section,
            "pages": pages,
            "text": "\n".join(current_text),
            "tables": attached_tables,
            "images": attached_images
        })

    for el in text_elements:

        el_type = el["type"]
        el_text = el.get("text", "")
        el_page = el.get("page")

        if el_type == "Title":

            flush_chunk()

            current_section = el_text.strip()
            current_text = []
            current_pages = set()

        elif el_type == "NarrativeText":

            if not current_section:
                continue

            current_text.append(el_text)

            if el_page is not None:
                current_pages.add(el_page)

    flush_chunk()

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":

    build_chunks(
        text_path="data/processed/text_elements.json",
        tables_index_path="data/processed/tables_index.json",
        images_path="data/processed/image_semantics.json",
        output_path="data/processed/chunks.json"
    )
