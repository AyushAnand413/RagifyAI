import json
import os

def route_elements(input_path: str, output_dir: str):
    with open(input_path, "r", encoding="utf-8") as f:
        elements = json.load(f)

    text_elements = []
    table_elements = []
    image_elements = []
    unknown_elements = []

    for el in elements:
        el_type = el.get("type")

        if "metadata" not in el or el["metadata"] is None:
            el["metadata"] = {}

        el["metadata"]["routed_as"] = el_type

        if el_type in ["Title", "NarrativeText"]:
            text_elements.append(el)

        elif el_type == "Table":
            table_elements.append(el)

        elif el_type == "Image":
            image_elements.append(el)

        else:
            unknown_elements.append(el)

    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, "text_elements.json"), "w", encoding="utf-8") as f:
        json.dump(text_elements, f, indent=2, ensure_ascii=False)

    with open(os.path.join(output_dir, "table_elements.json"), "w", encoding="utf-8") as f:
        json.dump(table_elements, f, indent=2, ensure_ascii=False)

    with open(os.path.join(output_dir, "image_elements.json"), "w", encoding="utf-8") as f:
        json.dump(image_elements, f, indent=2, ensure_ascii=False)

    with open(os.path.join(output_dir, "unknown_elements.json"), "w", encoding="utf-8") as f:
        json.dump(unknown_elements, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    route_elements(
        input_path="data/processed/parsed_elements.json",
        output_dir="data/processed"
    )
