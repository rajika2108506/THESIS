import os
import json
import ollama
from retrieve_context import retrieve_context
import chromadb

CHROMA_DIR = "chroma_db"
OUTPUT_DIR = "outputs"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# --------------------------------------------------
# Get current document_id from Chroma automatically
# --------------------------------------------------
def get_current_document_id():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_collection("cassation_judgments")
    result = collection.get(limit=1)
    return result["metadatas"][0]["document_id"]


# --------------------------------------------------
# Build strict JSON prompt
# --------------------------------------------------
def build_prompt(context):

    return f"""
You are a legal information extraction system.

Extract the following fields from the judgment text.

Return ONLY valid JSON.
If information is not present, write "not mentioned".

Required JSON format:

{{
  "PROCEEDING_ID_RGN": "",
  "VICTIM_ID": "",
  "SUSPECT_ID": "",
  "CRIME_ARTICLE": "",
  "VICTIM_OFFENDER RELATIONSHIP": "",
  "SPECIFIC_PLACE_OF_CRIME": ""
}}

Judgment Text:
{context}
"""


# --------------------------------------------------
# Main Extraction Function
# --------------------------------------------------
def extract_fields():

    document_id = get_current_document_id()

    # Broad legal query to retrieve relevant context
    query = "procedural details, victim, accused, crime article, victim-offender relationship, location of crime"

    chunks = retrieve_context(
        query=query,
        document_id=document_id,
        n_results=8
    )

    context = "\n\n".join(chunks)

    prompt = build_prompt(context)

    response = ollama.chat(
        model="llama3",  # your installed model
        messages=[{"role": "user", "content": prompt}],
        format="json",   # forces structured JSON
        options={"temperature": 0.1}
    )

    output_text = response["message"]["content"]

    try:
        parsed = json.loads(output_text)
    except:
        print("⚠ Model did not return valid JSON.")
        print(output_text)
        return

    output_path = os.path.join(
        OUTPUT_DIR,
        f"{document_id}_extraction.json"
    )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(parsed, f, indent=4, ensure_ascii=False)

    print("\n✅ Extraction complete.")
    print(f"Saved to: {output_path}")
    print("\nExtracted Data:\n")
    print(json.dumps(parsed, indent=4, ensure_ascii=False))


# --------------------------------------------------
# Run
# --------------------------------------------------
if __name__ == "__main__":
    extract_fields()
