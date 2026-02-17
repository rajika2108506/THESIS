import os
import json
import shutil
import chromadb
from sentence_transformers import SentenceTransformer

# ========= CONFIG =========
CHROMA_DIR = "chroma_db"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
# ===========================


def reset_chroma_db():
    """Delete old ChromaDB folder completely."""
    if os.path.exists(CHROMA_DIR):
        shutil.rmtree(CHROMA_DIR)
        print("Old ChromaDB deleted.")

    os.makedirs(CHROMA_DIR, exist_ok=True)


def ingest_file(input_json_path, document_id):
    """Ingest a single chunked JSON file into ChromaDB."""

    # 1️⃣ Reset DB
    reset_chroma_db()

    # 2️⃣ Create new persistent client
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    collection = client.create_collection(
        name="cassation_judgments"
    )

    # 3️⃣ Load embedding model
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    # 4️⃣ Load chunks
    with open(input_json_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    documents = []
    metadatas = []
    ids = []
    embeddings = []

    for idx, chunk in enumerate(chunks):
        text = chunk.get("text", "").strip()

        if not text:
            continue

        documents.append(text)

        metadatas.append({
            "document_id": document_id,
            "section": chunk.get("section", ""),
            "subsection": chunk.get("subsection", "")
        })

        ids.append(f"{document_id}_{idx}")

        embeddings.append(
            embedding_model.encode(text).tolist()
        )

    # 5️⃣ Add to collection
    if documents:
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings
        )

        print(f"Ingested {len(documents)} chunks.")
    else:
        print("No valid chunks found.")


# ========= RUN =========
if __name__ == "__main__":

    CHUNKS_DIR = "data/chunks"

    # Get all chunk files inside folder
    chunk_files = [
        f for f in os.listdir(CHUNKS_DIR)
        if f.endswith("_chunks.json")
    ]

    if not chunk_files:
        print("No chunk files found in data/chunks/")
        exit()

    if len(chunk_files) > 1:
        print("Warning: More than one chunk file found.")
        print("Only the first one will be processed.")

    selected_file = chunk_files[0]
    input_path = os.path.join(CHUNKS_DIR, selected_file)

    # Automatically derive document_id from filename
    document_id = selected_file.replace("_chunks.json", "")

    ingest_file(
        input_json_path=input_path,
        document_id=document_id
    )

    print(f"Ingestion complete for: {selected_file}")
