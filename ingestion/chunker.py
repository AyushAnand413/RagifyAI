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

    # Provide a mutable list to hold our scalar counter
    # This avoids "chunk_id is not mutable from the current scope" errors
    chunk_id = [0]

    def flush_chunk():
        if not current_section or not current_text:
            return

        pages = sorted(list(current_pages))

        attached_tables = [
            t.get("id")
            for t in tables_index
            if t.get("page") in pages
        ]

        attached_images = [
            {
                "page": img.get("page"),
                "caption": img.get("caption", "")
            }
            for img in images
            if img.get("page") in pages
        ]

        full_text = "\n".join(current_text)
        words = full_text.replace('\n', ' \n ').split(' ')
        words = [w for w in words if w != '']
        
        MAX_WORDS = 300
        OVERLAP = 50
        
        if not words:
            return
            
        i = 0
        part = 1
        while i < len(words):
            chunk_words = words[i:i + MAX_WORDS]
            split_text = " ".join(chunk_words).replace(' \n ', '\n').strip()
            
            chunk_id[0] += 1

            chunks.append({
                "chunk_id": f"chunk_{chunk_id[0]:03d}",
                "section": f"{current_section} (Part {part})" if len(words) > MAX_WORDS else current_section,
                "pages": pages,
                "text": split_text,
                "tables": attached_tables,
                "images": attached_images
            })
            
            part += 1
            i += MAX_WORDS - OVERLAP

    for el in text_elements:

        el_type = el.get("type", "Text")
        el_text = el.get("text", "")
        el_page = el.get("page")

        if el_type == "Title":

            flush_chunk()

            current_section = el_text.strip()
            current_text = []
            current_pages = set()

        elif el_type in ["NarrativeText", "ListItem", "Text"]:

            if not current_section:
                # Fallback to a default section to prevent discarding early text
                current_section = "General"

            if el_type == "ListItem":
                current_text.append(f"- {el_text}")
            else:
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
