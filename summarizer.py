import json
import glob
import os


def generate_summary(output_folder):
    """Generate financial summary from all receipt JSONs."""
    
    files = glob.glob(os.path.join(output_folder, "*.json"))
    
    total_spend = 0.0
    num_transactions = 0
    store_spend = {}
    failed_receipts = []
    
    for filepath in files:
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            
            store = data.get("store_name", {}).get("value", "Unknown")
            amount_str = data.get("total_amount", {}).get("value", "")
            
            if amount_str and amount_str != "NOT_FOUND":
                amount = float(
                    str(amount_str).replace(",", ".").replace("$", "")
                )
                total_spend += amount
                num_transactions += 1
                store_spend[store] = round(
                    store_spend.get(store, 0.0) + amount, 2
                )
            else:
                failed_receipts.append(os.path.basename(filepath))
        
        except Exception as e:
            failed_receipts.append(os.path.basename(filepath))
            print(f"Error reading {filepath}: {e}")
    
    summary = {
        "total_spend": round(total_spend, 2),
        "num_transactions": num_transactions,
        "spend_per_store": store_spend,
        "receipts_with_missing_total": failed_receipts
    }
    
    return summary