import json
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

# -------------------------------
# LOAD BLIP ONCE
# -------------------------------

processor = BlipProcessor.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)
model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)

# -------------------------------
# CAPTION GENERATION
# -------------------------------

def generate_caption(image_path: str) -> str:
    try:
        image = Image.open(image_path).convert("RGB")
        inputs = processor(image, return_tensors="pt")
        out = model.generate(**inputs, max_new_tokens=50)
        return processor.decode(out[0], skip_special_tokens=True)
    except Exception:
        return ""

# -------------------------------
# INFORMATIVE VS DECORATIVE
# -------------------------------

def is_informative(caption: str) -> bool:
    if not caption or len(caption.strip()) < 10:
        return False

    keywords = [
        "chart", "graph", "revenue", "growth",
        "performance", "financial", "trend",
        "figure", "data"
    ]

    caption = caption.lower()
    return any(k in caption for k in keywords)

# -------------------------------
# MAIN FILTER PIPELINE
# -------------------------------

def filter_images(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        images = json.load(f)

    informative = []

    for img in images:
        image_path = img.get("metadata", {}).get("image_path")

        # Safety: skip invalid records
        if not image_path or img.get("page") is None:
            continue

        caption = generate_caption(image_path)

        if is_informative(caption):
            informative.append({
                "id": img["id"],
                "page": img["page"],
                "order": img["order"],
                "image_path": image_path,
                "caption": caption
            })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(informative, f, indent=2, ensure_ascii=False)

# -------------------------------
# CLI ENTRYPOINT
# -------------------------------

if __name__ == "__main__":
    filter_images(
        input_path="data/processed/image_elements.json",
        output_path="data/processed/informative_images.json"
    )
