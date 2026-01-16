import json
from paddleocr import PaddleOCR

# -------------------------------
# OCR ENGINE (LOAD ONCE)
# -------------------------------

ocr_engine = PaddleOCR(use_angle_cls=True, lang="en")

# -------------------------------
# OCR (RAW SIGNAL ONLY)
# -------------------------------

def extract_ocr(image_path: str):
    try:
        result = ocr_engine.ocr(image_path, cls=True)
        texts = []

        for line in result:
            for word in line:
                texts.append(word[1][0])

        return texts
    except Exception:
        return []

# -------------------------------
# MAIN PIPELINE
# -------------------------------

def process_images(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8") as f:
        images = json.load(f)

    processed_images = []

    for img in images:
        image_path = img.get("image_path")

        # Safety check
        if not image_path or img.get("page") is None:
            continue

        ocr_text = extract_ocr(image_path)

        processed_images.append({
            "id": img["id"],
            "page": img["page"],
            "order": img["order"],
            "image_path": image_path,
            "caption": img["caption"],
            "ocr_raw_text": ocr_text,
            "semantic_summary":
                "The image provides a visual representation of trends or metrics relevant to company performance."
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(processed_images, f, indent=2, ensure_ascii=False)

# -------------------------------
# CLI ENTRYPOINT
# -------------------------------

if __name__ == "__main__":
    process_images(
        input_path="data/processed/informative_images.json",
        output_path="data/processed/image_semantics.json"
    )
