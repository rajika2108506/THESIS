def build_prompt(context, field_name):
    return f"""
You are analyzing an Italian criminal court judgment.

Context:
{context}

Task:
Extract the following information:
{field_name}

Rules:
- If explicitly stated, mark as "explicit"
- If inferred from context, mark as "inferred"
- If not present, return "not mentioned"

Return a JSON object.
"""
