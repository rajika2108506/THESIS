import os
import json
import re
import ollama
import chromadb
from retrieve_context import retrieve_context

CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "cassation_judgments"
OUTPUT_DIR = "outputs"

os.makedirs(OUTPUT_DIR, exist_ok=True)

REQUIRED_KEYS = {
    "PROCEEDING_ID_RGN",
    "VICTIM_ID",
    "SUSPECT_ID",
    "CRIME_ARTICLE",
    "VICTIM_OFFENDER_RELATIONSHIP",
    "SPECIFIC_PLACE_OF_CRIME"
}


# --------------------------------------------------
# Get current document_id
# --------------------------------------------------
def get_current_document_id():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_collection(COLLECTION_NAME)

    result = collection.get(limit=1)

    if not result["metadatas"]:
        raise ValueError("No document found in Chroma.")

    return result["metadatas"][0]["document_id"]


# --------------------------------------------------
# Get FULL document text
# --------------------------------------------------
def get_full_document_text(document_id):
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_collection(COLLECTION_NAME)

    results = collection.get(where={"document_id": document_id})
    documents = results.get("documents", [])

    return "\n".join(documents)


# --------------------------------------------------
# Normalize Output
# --------------------------------------------------
def normalize_output(parsed_json):
    for key in REQUIRED_KEYS:
        if key not in parsed_json:
            parsed_json[key] = "not mentioned"
        elif not parsed_json[key] or parsed_json[key].strip() == "":
            parsed_json[key] = "not mentioned"
    return parsed_json


# --------------------------------------------------
# Clean Multiple Names
# --------------------------------------------------
def clean_multiple_names(text):
    if text == "not mentioned":
        return text

    names = [n.strip() for n in text.split(",")]
    names = list(dict.fromkeys(names))  # remove duplicates, keep order
    return ", ".join(names)


# --------------------------------------------------
# Validate Crime Article
# --------------------------------------------------
def validate_crime_article(text):
    if not text:
        return "not mentioned"

    text_lower = text.lower()

    if re.search(r'\bart\.?\s*\d+', text_lower) or \
       "cod. pen" in text_lower or \
       "c.p." in text_lower:
        return text.strip()

    return "not mentioned"


# --------------------------------------------------
# Validate Relationship
# --------------------------------------------------
def validate_relationship(text):
    if not text:
        return "not mentioned"

    text = text.strip()
    text_lower = text.lower()

    # Reject meaningless structures
    if "in danno di" in text_lower:
        return "not mentioned"

    # Reject if contains full name
    if re.search(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', text):
        return "not mentioned"

    # Reject long descriptive phrases
    if len(text.split()) > 3:
        return "not mentioned"

    allowed_relationships = [
        "convivente",
        "ex convivente",
        "coniuge",
        "marito",
        "moglie",
        "figlio",
        "figlia",
        "padre",
        "madre",
        "fratello",
        "sorella",
        "compagno",
        "compagna",
        "partner",
        "CONIUGE",
        "SEPARATO",
        "DIVORZIATO",
        "CONVIVENTE",
        "EX CONVIVENTE",
        "FIDANZATO",
        "EX FIDANZATO",
        "PARTNER",
        "EX PARTNER",
        "AMANTE",
        "EX AMANTE",
        "PADRE",
        "MADRE",
        "FIGLIO",
        "FRATELLO",
        "NONNO",
        "ZIO",
        "NIPOTE",
        "ALTRO GRADO",
        "AMICO",
        "EX AMICO",
        "VICINO DI CASA",
        "EX VICINO DI CASA",
        "COLLEGA",
        "EX COLLEGA",
        "DATORE DI LAVORO",
        "EX DATORE DI LAVORO",
        "SUPERIORE GERARCHICO",
        "EX SUPERIORE GERARCHICO",
        "DIPENDENTE",
        "EX DIPENDENTE"
    ]

    for rel in allowed_relationships:
        if rel in text_lower:
            return rel

    return "not mentioned"


# --------------------------------------------------
# Prompt Builder
# --------------------------------------------------
def build_prompt(context):

    return f"""
You are a strict legal information extraction engine.

STRICT RULES:
- Output ONLY valid JSON.
- Use EXACTLY the provided keys.
- Do NOT add extra keys.
- Do NOT rename keys.
- Do NOT explain.
- Extract exact spans only.
- If unclear, write "not mentioned".

IMPORTANT ROLE RULES:

For VICTIM_ID:
- Extract ONLY the person explicitly identified as "persona offesa", "parte civile", or victim.
- Do NOT extract the accused.
- If multiple victims exist, separate names with comma.

For SUSPECT_ID:
- Extract ONLY the accused/imputato/ricorrente.
- If multiple suspects exist, separate names with comma.
- Do NOT confuse with victim.

For CRIME_ARTICLE:
- Return ONLY formal legal references (e.g., art. 572 cod. pen.)
- Do NOT return descriptions.

For VICTIM_OFFENDER_RELATIONSHIP:
- Return ONLY one legal role word (convivente, coniuge, figlio, etc.)
- No names.
- No phrases.
- If unclear, return "not mentioned".

Required JSON schema:

{{
  "PROCEEDING_ID_RGN": "",
  "VICTIM_ID": "",
  "SUSPECT_ID": "",
  "CRIME_ARTICLE": "",
  "VICTIM_OFFENDER_RELATIONSHIP": "",
  "SPECIFIC_PLACE_OF_CRIME": ""
}}

Judgment Text:
{context}
"""


# --------------------------------------------------
# Schema Validation
# --------------------------------------------------
def validate_schema(parsed_json):
    return set(parsed_json.keys()) == REQUIRED_KEYS


# --------------------------------------------------
# MAIN EXTRACTION
# --------------------------------------------------
def extract_fields():

    document_id = get_current_document_id()
    print("Retrieving relevant context...")

    query = """
R.G.N. 12345/2022,
numero R.G.N.,
persona offesa,
imputato,
art. cod. pen.,
rapporto tra imputato e persona offesa,
luogo del fatto
"""

    chunks = retrieve_context(
        query=query,
        document_id=document_id,
        n_results=4
    )

    if not chunks:
        print("⚠ No relevant chunks retrieved.")
        return

    context = "\n\n".join(chunks)
    full_text = get_full_document_text(document_id)

    # RGN authoritative via regex
    rgn_match = re.search(r"R\.G\.N\.\s*\d+/\d{4}", full_text)
    rgn_regex = rgn_match.group() if rgn_match else None

    prompt = build_prompt(context)

    print("Calling LLM...")

    response = ollama.chat(
        model="llama3:latest",
        messages=[
            {"role": "system", "content": "You are a strict JSON extraction engine."},
            {"role": "user", "content": prompt}
        ],
        format="json",
        options={
            "temperature": 0,
            "num_predict": 350
        }
    )

    try:
        parsed = json.loads(response["message"]["content"])
    except:
        print("⚠ Invalid JSON returned.")
        print(response["message"]["content"])
        return

    # Ensure schema compliance
    if not validate_schema(parsed):
        parsed = normalize_output(parsed)

    parsed = normalize_output(parsed)

    # Override RGN if found via regex
    if rgn_regex:
        parsed["PROCEEDING_ID_RGN"] = rgn_regex

    # Clean names
    parsed["SUSPECT_ID"] = clean_multiple_names(parsed["SUSPECT_ID"])
    parsed["VICTIM_ID"] = clean_multiple_names(parsed["VICTIM_ID"])

    # Prevent same person in both roles
    if parsed["VICTIM_ID"] == parsed["SUSPECT_ID"]:
        parsed["VICTIM_ID"] = "not mentioned"

    # Field validations
    parsed["CRIME_ARTICLE"] = validate_crime_article(parsed["CRIME_ARTICLE"])
    parsed["VICTIM_OFFENDER_RELATIONSHIP"] = validate_relationship(
        parsed["VICTIM_OFFENDER_RELATIONSHIP"]
    )

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
# RUN
# --------------------------------------------------
if __name__ == "__main__":
    extract_fields()