import os
import json
import re
from collections import Counter

PRED_DIR = "outputs"
GOLD_DIR = "data/ground_truth"

FIELDS = [
    "PROCEEDING_ID_RGN",
    "VICTIM_ID",
    "SUSPECT_ID",
    "CRIME_ARTICLE",
    "VICTIM_OFFENDER_RELATIONSHIP",
    "SPECIFIC_PLACE_OF_CRIME"
]

# --------------------------------------------------
# Semantic Normalization Dictionary
# (Add more if needed)
# --------------------------------------------------
SEMANTIC_MAP = {
    "convivente": "cohabitant",
    "cohabitant": "cohabitant",
    "ex convivente": "former cohabitant",
    "maltrattamenti": "domestic violence",
    "violenza domestica": "domestic violence",
    "moglie": "spouse"
    
}


# --------------------------------------------------
# Basic Text Normalization
# --------------------------------------------------
def normalize(text):
    if not text:
        return ""
    text = str(text).lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    # Apply semantic mapping
    for k, v in SEMANTIC_MAP.items():
        text = text.replace(k, v)

    return text


# --------------------------------------------------
# RGN Normalization (numeric pattern only)
# --------------------------------------------------
def normalize_rgn(text):
    if not text:
        return ""
    match = re.search(r'\d+/\d{4}', str(text))
    if match:
        return match.group(0)
    return ""


# --------------------------------------------------
# Tokenization
# --------------------------------------------------
def tokenize(text):
    return normalize(text).split()


# --------------------------------------------------
# Compute Precision / Recall / F1
# --------------------------------------------------
def compute_scores(tp, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    return precision, recall, f1


# --------------------------------------------------
# Main Evaluation
# --------------------------------------------------
def evaluate():

    exact_results = {field: {"tp": 0, "fp": 0, "fn": 0} for field in FIELDS}
    token_results = {field: {"tp": 0, "fp": 0, "fn": 0} for field in FIELDS}

    files = [f for f in os.listdir(GOLD_DIR) if f.endswith(".json")]

    for file in files:

        gold_path = os.path.join(GOLD_DIR, file)
        pred_path = os.path.join(PRED_DIR, file)

        if not os.path.exists(pred_path):
            print(f"⚠ Missing prediction for {file}")
            continue

        with open(gold_path, "r", encoding="utf-8") as f:
            gold = json.load(f)

        with open(pred_path, "r", encoding="utf-8") as f:
            pred = json.load(f)

        for field in FIELDS:

            gold_raw = gold.get(field, "")
            pred_raw = pred.get(field, "")

            # -----------------------------
            # Special handling for RGN
            # -----------------------------
            if field == "PROCEEDING_ID_RGN":
                gold_value = normalize_rgn(gold_raw)
                pred_value = normalize_rgn(pred_raw)
            else:
                gold_value = normalize(gold_raw)
                pred_value = normalize(pred_raw)

            # =============================
            # EXACT MATCH
            # =============================
            if gold_value == pred_value and gold_value != "":
                exact_results[field]["tp"] += 1
            elif gold_value != "" and pred_value == "":
                exact_results[field]["fn"] += 1
            elif gold_value != pred_value:
                exact_results[field]["fp"] += 1

            # =============================
            # TOKEN-LEVEL
            # =============================
            gold_tokens = tokenize(gold_raw) if field != "PROCEEDING_ID_RGN" else [gold_value]
            pred_tokens = tokenize(pred_raw) if field != "PROCEEDING_ID_RGN" else [pred_value]

            gold_counter = Counter(gold_tokens)
            pred_counter = Counter(pred_tokens)

            common = gold_counter & pred_counter
            overlap = sum(common.values())

            tp = overlap
            fp = len(pred_tokens) - overlap
            fn = len(gold_tokens) - overlap

            token_results[field]["tp"] += tp
            token_results[field]["fp"] += fp
            token_results[field]["fn"] += fn

    # --------------------------------------------------
    # Print Results
    # --------------------------------------------------
    print("\n====================================")
    print(" EXACT MATCH EVALUATION")
    print("====================================\n")

    for field in FIELDS:
        tp = exact_results[field]["tp"]
        fp = exact_results[field]["fp"]
        fn = exact_results[field]["fn"]

        precision, recall, f1 = compute_scores(tp, fp, fn)

        print(field)
        print(f"Precision: {precision:.3f}")
        print(f"Recall:    {recall:.3f}")
        print(f"F1 Score:  {f1:.3f}")
        print("------------------------------------")

    print("\n====================================")
    print(" TOKEN-LEVEL EVALUATION")
    print("====================================\n")

    for field in FIELDS:
        tp = token_results[field]["tp"]
        fp = token_results[field]["fp"]
        fn = token_results[field]["fn"]

        precision, recall, f1 = compute_scores(tp, fp, fn)

        print(field)
        print(f"Precision: {precision:.3f}")
        print(f"Recall:    {recall:.3f}")
        print(f"F1 Score:  {f1:.3f}")
        print("------------------------------------")


if __name__ == "__main__":
    evaluate()