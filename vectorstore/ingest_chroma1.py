import os
import json
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

CHUNKS_DIR = "data/chunks"
CHROMA_DIR = "chroma_db"

os.makedirs(CHROMA_DIR, exist_ok=True)

# Embedding model (local)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

#  Persistent Chroma client (IMPORTANT)
client = chromadb.PersistentClient(
    path=CHROMA_DIR
)

collection = client.get_or_create_collection(
    name="cassation_judgments"
)

def ingest_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    documents = []
    metadatas = []
    ids = []

    for idx, chunk in enumerate(chunks):
        text = chunk.get("text", "").strip()
        if not text:
            continue

        documents.append(text)
        metadatas.append({
            "document_id": chunk["document_id"],
            "section": chunk["section"],
            "subsection": chunk["subsection"]
        })
        ids.append(f"{chunk['document_id']}_{idx}")

    if documents:
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

def main():
    for filename in os.listdir(CHUNKS_DIR):
        if filename.endswith("_chunks.json"):
            filepath = os.path.join(CHUNKS_DIR, filename)
            ingest_file(filepath)
            print(f"Ingested: {filename}")

    print("ChromaDB persistent storage complete.")

if __name__ == "__main__":
    main()
