import chromadb

# Load persistent ChromaDB
client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_collection(name="cassation_judgments")

print("Total chunks in DB:", collection.count())

# Test query (Italian legal context)
query = "ex convivente minacce e molestie"

results = collection.query(
    query_texts=[query],
    n_results=5
)

# Print results
for i, doc in enumerate(results["documents"][0], start=1):
    metadata = results["metadatas"][0][i-1]
    print(f"\nResult {i}")
    print("Section:", metadata["section"])
    print("Subsection:", metadata["subsection"])
    print("Text preview:", doc[:400])
