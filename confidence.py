import re

LOW_CONFIDENCE_THRESHOLD = 0.7


def get_avg_confidence(text, ocr_results):
    """Get average OCR confidence for words matching the text."""
    if not text:
        return 0.4
    scores = []
    for r in ocr_results:
        if r["text"].lower() in str(text).lower():
            scores.append(r["confidence"])
    return sum(scores) / len(scores) if scores else 0.5


def compute_field_confidence(value, ocr_conf, pattern_matched,
                              keyword_matched=False):
    """Combine OCR confidence with validation signals."""
    if value is None:
        return 0.0
    
    score = ocr_conf
    if pattern_matched:
        score += 0.10
    if keyword_matched:
        score += 0.05
    if not pattern_matched and not keyword_matched:
        score -= 0.15
    
    return round(min(1.0, max(0.0, score)), 2)


def build_output_with_confidence(store, date, total,
                                  items, ocr_results):
    """Build the final structured JSON with confidence scores."""
    
    # Check patterns
    date_pattern = bool(date and re.search(
        r'\d{1,4}[\-\/\.]\d{1,2}[\-\/\.]\d{1,4}', str(date)
    ))
    total_pattern = bool(total and re.search(
        r'^\d+\.\d{2}$', str(total)
    ))
    
    # Compute confidences
    store_conf = compute_field_confidence(
        store,
        get_avg_confidence(store, ocr_results),
        len(str(store)) > 3,
        False
    )
    date_conf = compute_field_confidence(
        date,
        get_avg_confidence(date, ocr_results),
        date_pattern,
        False
    )
    total_conf = compute_field_confidence(
        total,
        get_avg_confidence(total, ocr_results),
        total_pattern,
        True
    )
    
    def flag(conf):
        return "LOW_CONFIDENCE" if conf < LOW_CONFIDENCE_THRESHOLD \
               else "OK"
    
    output = {
        "store_name": {
            "value": store or "UNKNOWN",
            "confidence": store_conf,
            "flag": flag(store_conf)
        },
        "date": {
            "value": date or "NOT_FOUND",
            "confidence": date_conf,
            "flag": flag(date_conf)
        },
        "total_amount": {
            "value": total or "NOT_FOUND",
            "confidence": total_conf,
            "flag": flag(total_conf)
        },
        "items": items
    }
    
    return output