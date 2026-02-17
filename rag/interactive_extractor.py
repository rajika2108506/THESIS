import ollama
from retrieve_context import retrieve_context

import chromadb

def get_current_document_id():
    client = chromadb.PersistentClient(path="chroma_db")
    collection = client.get_collection("cassation_judgments")

    # get first stored metadata
    result = collection.get(limit=1)
    return result["metadatas"][0]["document_id"]

DOCUMENT_ID = get_current_document_id()



SYSTEM_PROMPT = """
You are a legal information extraction assistant.
You analyze one Italian Cassation Court judgment.

Answer strictly using the provided context.
If information is implicit, infer carefully.
If not present, say "not mentioned".

Always justify your answer briefly.
"""


def ask_question(question):

    # Retrieve relevant chunks
    chunks = retrieve_context(
        query=question,
        document_id=DOCUMENT_ID,
        n_results=5
    )

    context = "\n\n".join(chunks)

    prompt = f"""
    Context:
    {context}

    Question:
    {question}
    """

    response = ollama.chat(
        model="llama3:latest",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        options={
            "temperature": 0.2
        }
    )

    return response["message"]["content"]


def interactive_loop():
    print("\nInteractive Legal Extraction Started.")
    print("Type 'exit' to stop.\n")

    while True:
        question = input("Ask a field or question: ")

        if question.lower() == "exit":
            break

        answer = ask_question(question)

        print("\n--- ANSWER ---")
        print(answer)
        print("\n")


if __name__ == "__main__":
    interactive_loop()
