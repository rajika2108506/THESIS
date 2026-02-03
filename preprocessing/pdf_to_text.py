import pdfplumber
import os

INPUT_DIR = "data/raw_pdfs"
OUTPUT_DIR = "data/text_raw"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_raw_text(pdf_path):
    pages_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)
    return "\n".join(pages_text)

for filename in os.listdir(INPUT_DIR):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(
            OUTPUT_DIR, filename.replace(".pdf", ".txt")
        )

        raw_text = extract_raw_text(pdf_path)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(raw_text)

        print(f"Raw text saved: {output_path}")
