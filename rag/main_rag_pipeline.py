from retrieve_context import retrieve_context
from prompt_templates import build_prompt
import ollama

query = "What is the relationship between victim and offender?"

chunks = retrieve_context(query, section="FATTO")
context = "\n\n".join(chunks)

prompt = build_prompt(context, "victim–offender relationship")

response = ollama.chat(
    model="llama3",
    messages=[{"role": "user", "content": prompt}]
)

print("\n--- LLM OUTPUT ---\n")
print(response["message"]["content"])
