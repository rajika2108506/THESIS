import chromadb

def retrieve_context(query, section=None, n_results=5):
    client = chromadb.PersistentClient(path="chroma_db")
    collection = client.get_collection("cassation_judgments")

    where_clause = {"section": section} if section else None

    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where=where_clause
    )

    return results["documents"][0]
