# llm_runner.py

import ollama
import json

def run_llm(prompt, model="llama3"):
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response["message"]["content"]

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "value": "error",
            "confidence": "error",
            "evidence": raw
        }
