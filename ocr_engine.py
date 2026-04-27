import easyocr

# Initialize reader once (downloads model on first run ~200MB)
reader = easyocr.Reader(['en'], gpu=False)


def run_ocr(image_path):
    """Run OCR and return list of text + confidence results."""
    try:
        results = reader.readtext(image_path)
        extracted = []
        for (bbox, text, confidence) in results:
            if text.strip():  # skip empty text
                extracted.append({
                    "text": text.strip(),
                    "confidence": round(float(confidence), 4),
                    "bbox": [list(point) for point in bbox]
                })
        return extracted
    except Exception as e:
        print(f"OCR error: {e}")
        return []