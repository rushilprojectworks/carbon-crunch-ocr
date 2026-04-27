import re


def extract_fields(ocr_results):
    """Extract store name, date, total, and items from OCR results."""
    
    lines = [r["text"] for r in ocr_results]
    full_text = " ".join(lines)
    
    # ── Store Name ──────────────────────────────────────────
    # Usually the first non-empty, reasonably long line
    store_name = None
    for line in lines[:5]:
        if len(line) > 2 and not re.match(r'^\d+$', line):
            store_name = line
            break
    
    # ── Date ─────────────────────────────────────────────────
    date_patterns = [
        r'\b\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}\b',   # 12/05/2024
        r'\b\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2}\b',      # 2024-05-12
        r'\b\d{1,2}\s+\w{3,9}\s+\d{2,4}\b',               # 12 May 2024
        r'\b\w{3,9}\s+\d{1,2},?\s+\d{4}\b',               # May 12, 2024
    ]
    date = None
    for pattern in date_patterns:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            date = match.group()
            break
    
    # ── Total Amount ──────────────────────────────────────────
    total_patterns = [
        r'(?:total|grand\s*total|amount\s*due|total\s*amount|'
        r'balance\s*due|net\s*total)[^\d]*(\d+[\.,]\d{2})',
        r'(?:total)[^\d]*\$?\s*(\d+[\.,]\d{2})',
    ]
    total = None
    for pattern in total_patterns:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            total = match.group(1).replace(',', '.')
            break
    
    # Fallback: find largest price-like number in text
    if not total:
        prices = re.findall(r'\d+[\.,]\d{2}', full_text)
        if prices:
            numeric = [float(p.replace(',', '.')) for p in prices]
            total = str(max(numeric))
    
    # ── Items ─────────────────────────────────────────────────
    items = []
    item_pattern = re.compile(
        r'^(.{3,40}?)\s{2,}(\d+[\.,]\d{2})\s*$'
    )
    skip_keywords = ['total', 'tax', 'subtotal', 'vat',
                     'change', 'cash', 'card', 'thank']
    
    for line in lines:
        match = item_pattern.match(line.strip())
        if match:
            name = match.group(1).strip()
            price = match.group(2)
            if not any(kw in name.lower() for kw in skip_keywords):
                items.append({
                    "name": name,
                    "price": price.replace(',', '.')
                })
    
    return store_name, date, total, items