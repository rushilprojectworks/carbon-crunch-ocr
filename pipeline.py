import os
import json
import cv2

from preprocessing import preprocess_image
from ocr_engine import run_ocr
from extractor import extract_fields
from confidence import build_output_with_confidence
from summarizer import generate_summary

IMAGE_DIR = "data/"
OUTPUT_DIR = "outputs/"
TEMP_IMAGE = "temp_preprocessed.png"

os.makedirs(OUTPUT_DIR, exist_ok=True)

SUPPORTED_FORMATS = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp')


def process_all_receipts():
    image_files = [
        f for f in os.listdir(IMAGE_DIR)
        if f.lower().endswith(SUPPORTED_FORMATS)
    ]
    
    if not image_files:
        print("❌ No images found in data/ folder!")
        return
    
    print(f"✅ Found {len(image_files)} receipt images\n")
    
    for img_file in image_files:
        print(f"Processing: {img_file}")
        img_path = os.path.join(IMAGE_DIR, img_file)
        
        try:
            # Step 1: Preprocess
            clean = preprocess_image(img_path)
            cv2.imwrite(TEMP_IMAGE, clean)
            
            # Step 2: OCR
            ocr_results = run_ocr(TEMP_IMAGE)
            
            if not ocr_results:
                print(f"  ⚠️  No text detected in {img_file}")
                continue
            
            # Step 3: Extract fields
            store, date, total, items = extract_fields(ocr_results)
            
            # Step 4: Build confident output
            output = build_output_with_confidence(
                store, date, total, items, ocr_results
            )
            
            # Step 5: Save JSON
            base_name = os.path.splitext(img_file)[0]
            out_path = os.path.join(OUTPUT_DIR, f"{base_name}.json")
            with open(out_path, "w") as f:
                json.dump(output, f, indent=2)
            
            print(f"  ✅ Saved → {out_path}")
        
        except Exception as e:
            print(f"  ❌ Failed: {img_file} — {e}")
    
    # Step 6: Generate summary
    print("\n📊 Generating financial summary...")
    summary = generate_summary(OUTPUT_DIR)
    
    summary_path = os.path.join(OUTPUT_DIR, "summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"✅ Summary saved → {summary_path}")
    print("\n===== SUMMARY =====")
    print(json.dumps(summary, indent=2))
    
    # Cleanup
    if os.path.exists(TEMP_IMAGE):
        os.remove(TEMP_IMAGE)


if __name__ == "__main__":
    process_all_receipts()