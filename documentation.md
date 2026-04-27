# Carbon Crunch OCR Assignment — Documentation

## Approach
1. **Preprocessing**: Each receipt image is converted to grayscale,
   denoised using OpenCV's fastNlMeansDenoising, contrast-enhanced
   with CLAHE, deskewed using minAreaRect rotation correction,
   and binarized using Otsu thresholding.

2. **OCR**: EasyOCR (English) was used for text recognition as it
   handles noisy, real-world images well and natively returns
   per-detection confidence scores.

3. **Extraction**: Regex patterns extract dates, total amounts,
   and item-price pairs. Store name is heuristically inferred
   from the first prominent line.

4. **Confidence Scoring**: Each field gets a score combining
   OCR confidence + pattern match bonus/penalty. Fields below
   0.7 are flagged as LOW_CONFIDENCE.

5. **Summary**: All JSONs are aggregated to compute total spend,
   transaction count, and per-store breakdown.

## Tools Used
- Python 3.10
- EasyOCR — OCR engine with confidence scores
- OpenCV — Image preprocessing
- Regex — Pattern-based field extraction

## Challenges Faced
- Varied receipt layouts made universal regex patterns difficult
- Some receipts had extremely low contrast requiring aggressive CLAHE
- Store names are inconsistently placed across receipts
- Total amounts sometimes labeled differently (Balance Due, Net, etc.)

## Potential Improvements
- Fine-tune with a labeled receipt dataset (CORD, SROIE)
- Use LayoutLM or Donut model for layout-aware extraction
- Train a NER model specifically for receipt entities
- Add currency normalization and multi-language support