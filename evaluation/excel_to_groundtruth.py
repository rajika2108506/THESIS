import os
import json
import pandas as pd
import re

EXCEL_PATH = "data/manual_annotations.xlsx"
OUTPUT_DIR = "data/ground_truth"

REQUIRED_FIELDS = [
    "PROCEEDING_ID_RGN",
    "VICTIM_ID",
    "SUSPECT_ID",
    "CRIME_ARTICLE",
    "VICTIM_OFFENDER_RELATIONSHIP",
    "SPECIFIC_PLACE_OF_CRIME"
]


# --------------------------------------------------
# Clear old JSON files
# --------------------------------------------------
def clear_output_folder():
    if os.path.exists(OUTPUT_DIR):
        for f in os.listdir(OUTPUT_DIR):
            if f.endswith(".json"):
                os.remove(os.path.join(OUTPUT_DIR, f))
    else:
        os.makedirs(OUTPUT_DIR)


# --------------------------------------------------
# Normalize field values
# --------------------------------------------------
def normalize(value):
    if pd.isna(value):
        return "not mentioned"
    value = str(value).strip()
    if value == "":
        return "not mentioned"
    return value


# --------------------------------------------------
# Clean filename (Windows-safe)
# --------------------------------------------------
def clean_filename(name):

    name = str(name)

    # Remove newline characters
    name = name.replace("\n", "").replace("\r", "")

    # Remove illegal Windows characters
    name = re.sub(r'[<>:"/\\|?*]', "", name)

    name = name.strip()

    # Remove .pdf if present
    if name.endswith(".pdf"):
        name = name[:-4]

    return name


# --------------------------------------------------
# Main conversion
# --------------------------------------------------
def convert_transposed_excel():

    clear_output_folder()

    df = pd.read_excel(EXCEL_PATH)

    df.set_index("Colonna", inplace=True)

    document_columns = df.columns.tolist()

    filename_row = "FILE_NAME"

    if filename_row not in df.index:
        raise ValueError("FILE_NAME row not found in Excel.")

    for doc_col in document_columns:

        raw_filename = df.loc[filename_row, doc_col]

        document_id = clean_filename(raw_filename)

        if document_id == "" or document_id.lower() == "nan":
            print(f"⚠ Skipping empty filename column: {doc_col}")
            continue

        data = {}

        for field in REQUIRED_FIELDS:
            if field in df.index:
                value = df.loc[field, doc_col]
                data[field] = normalize(value)
            else:
                data[field] = "not mentioned"

        output_path = os.path.join(
            OUTPUT_DIR,
            f"{document_id}_extraction.json"
        )

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"Created: {output_path}")

    print("\n✅ Conversion completed successfully.")


if __name__ == "__main__":
    convert_transposed_excel()