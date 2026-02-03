import os
import re

INPUT_DIR = "data/text_raw"
OUTPUT_DIR = "data/text_clean"

os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADER_PATTERNS = [
    r"LA CORTE SUPREMA DI CASSAZIONE*",
    r"SESTA SEZIONE PENALE",
    r"Pagina\s+\d+"
]

def clean_text(text):
    # Fix hyphenation across line breaks (in-\ntervento → intervento)
    text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
    # Normalize whitespace
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)

    lines = text.split("\n")
    cleaned_lines = []

    # Very flexible detection of "Composta da"
    composed_pattern = re.compile(r"composta\s+da", re.IGNORECASE)
    end_pattern = re.compile(r"così\s+deciso\s+il", re.IGNORECASE)

    has_composed = any(
        composed_pattern.search(line.replace("\xa0", " "))
        for line in lines
    )

    start_keep = not has_composed
    stop_at_end = False

    for line in lines:
        # normalize spaces
        line = line.replace("\xa0", " ").strip()

        if end_pattern.search(line):
            break


        # Skip everything before "Composta da" IF it exists
        if not start_keep:
            if composed_pattern.search(line):
                start_keep = True
                cleaned_lines.append(line)  # keep the line
            continue
        
        if not line:
            continue

        if any(re.match(pattern, line, re.IGNORECASE) for pattern in HEADER_PATTERNS):
            continue

        if line.isdigit():
            continue

        cleaned_lines.append(line)

    # 🚨 SAFETY NET: never return empty text
    if not cleaned_lines:
        return "\n".join(
            line.strip() for line in lines if line.strip()
        )

    cleaned_text = "\n".join(cleaned_lines)
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)
    
    return cleaned_text



for filename in os.listdir(INPUT_DIR):
    if filename.endswith(".txt"):
        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(
            OUTPUT_DIR, filename.replace(".txt", "_clean.txt")
        )

        with open(input_path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        cleaned_text = clean_text(raw_text)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(cleaned_text)

        print(f"Cleaned text saved: {output_path}")
