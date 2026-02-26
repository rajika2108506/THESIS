import os
import json
import ollama
import chromadb
from retrieve_context import retrieve_context

CHROMA_DIR = "chroma_db"
OUTPUT_DIR = "outputs"
COLLECTION_NAME = "cassation_judgments"

os.makedirs(OUTPUT_DIR, exist_ok=True)

REQUIRED_KEYS = {
    "PROCEEDING_ID_RGN",
    "VICTIM_ID",
    "SUSPECT_ID",
    "CRIME_ARTICLE",
    "SPECIFIC_PLACE_OF_CRIME"
}


# --------------------------------------------------
# Get current document_id safely
# --------------------------------------------------
def get_current_document_id():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_collection(COLLECTION_NAME)

    result = collection.get(limit=1)

    if not result["metadatas"]:
        raise ValueError("No document found in Chroma.")

    return result["metadatas"][0]["document_id"]


# --------------------------------------------------
# Build strict prompt
# --------------------------------------------------
def build_prompt(context):

    return f"""
Extract ONLY the following fields from the legal judgment.

Return EXACTLY this JSON schema:

{{
  "PROCEEDING_ID_RGN": "",
  "VICTIM_ID": "",
  "SUSPECT_ID": "",
  "CRIME_ARTICLE": "",
  "SPECIFIC_PLACE_OF_CRIME": ""
}}

Rules:
- Do NOT add extra keys.
- Do NOT rename keys.
- Do NOT wrap inside another object.
- Do NOT use a key called "fields".
- If missing, write "not mentioned".
- Do NOT summarize.

Judgment Text:
{context}
"""


# --------------------------------------------------
# Validate JSON schema
# --------------------------------------------------
def validate_schema(parsed_json):
    return set(parsed_json.keys()) == REQUIRED_KEYS


# --------------------------------------------------
# Main extraction
# --------------------------------------------------
def extract_single_field(field_name, query, document_id):

    chunks = retrieve_context(
        query=query,
        document_id=document_id,
        n_results=2   # 🔥 small and precise
    )

    context = "\n\n".join(chunks)

    if not context.strip():
        return "not mentioned"

    prompt = f"""
Extract ONLY the value for: {field_name}

Rules:
- Return ONLY the extracted value.
- Do NOT explain.
- Do NOT summarize.
- If not found, return: not mentioned

Text:
{context}
"""

    response = ollama.chat(
        model="llama3:latest",
        messages=[
            {"role": "system", "content": "You extract exact factual values only."},
            {"role": "user", "content": prompt}
        ],
        options={
            "temperature": 0,
            "num_predict": 80  # 🔥 small response → faster
        }
    )

    return response["message"]["content"].strip()

def extract_fields():

    document_id = get_current_document_id()

    print("Extracting fields individually...")

    result = {}

    result["PROCEEDING_ID_RGN"] = extract_single_field(
        "Proceeding ID (R.G.N.)",
        "R.G.N. number of the proceeding",
        document_id
    )

    result["VICTIM_ID"] = extract_single_field(
        "Victim Identity",
        "name of the victim or injured person",
        document_id
    )

    result["SUSPECT_ID"] = extract_single_field(
        "Accused or suspect identity",
        "name of the accused or defendant",
        document_id
    )

    result["CRIME_ARTICLE"] = extract_single_field(
        "Crime Article",
        "article of the penal code violated",
        document_id
    )

    result["SPECIFIC_PLACE_OF_CRIME"] = extract_single_field(
        "Specific place of the crime",
        "location where the crime occurred",
        document_id
    )

    output_path = os.path.join(
        OUTPUT_DIR,
        f"{document_id}_extraction.json"
    )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print("\n✅ Extraction complete.")
    print(json.dumps(result, indent=4, ensure_ascii=False))
# --------------------------------------------------
# Run
# --------------------------------------------------
if __name__ == "__main__":
    extract_fields()