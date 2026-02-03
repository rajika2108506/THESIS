import os
import re
import json

INPUT_DIR = "data/text_clean"
OUTPUT_DIR = "data/chunks"

os.makedirs(OUTPUT_DIR, exist_ok=True)

MAX_CHARS = 1200

SECTION_PATTERNS = {
    "FATTO": re.compile(r"ritenuto\s+in\s+fatto", re.IGNORECASE),
    "DIRITTO": re.compile(r"considerato\s+in\s+diritto", re.IGNORECASE),
    "PQM": re.compile(r"p\.?\s*q\.?\s*m\.?", re.IGNORECASE),
}

# Numbered legal point pattern (1., 2), 3 - ...)
POINT_PATTERN = re.compile(r"^\s*(\d+)[\.\)\-]\s+", re.MULTILINE)


def split_into_sections(text):
    sections = {}
    current_section = "INTRO"
    sections[current_section] = []

    lines = text.split("\n")

    for line in lines:
        for section_name, pattern in SECTION_PATTERNS.items():
            if pattern.search(line):
                current_section = section_name
                sections[current_section] = []
                break
        else:
            sections[current_section].append(line)

    for key in sections:
        sections[key] = "\n".join(sections[key]).strip()

    return sections


def split_into_points(section_text):
    """
    Splits legal reasoning into numbered points (DIRITTO only).
    """
    points = []
    current_point = "0"
    buffer = []

    for line in section_text.split("\n"):
        match = POINT_PATTERN.match(line)
        if match:
            if buffer:
                points.append((current_point, "\n".join(buffer).strip()))
            current_point = match.group(1)
            buffer = [line]
        else:
            buffer.append(line)

    if buffer:
        points.append((current_point, "\n".join(buffer).strip()))

    return points


def chunk_by_paragraph(text, section, subsection, doc_id):
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []

    current_chunk = ""
    chunk_id = 1

    for para in paragraphs:
        if len(current_chunk) + len(para) <= MAX_CHARS:
            current_chunk += para + "\n\n"
        else:
            clean_text = current_chunk.strip()
            if clean_text:
                chunks.append({
                    "document_id": doc_id,
                    "section": section,
                    "subsection": subsection,
                    "chunk_id": f"{subsection}_{chunk_id}",
                    "text": clean_text
                })

          
            chunk_id += 1
            current_chunk = para + "\n\n"

    if current_chunk.strip():
        clean_text = current_chunk.strip()
        if clean_text:
            chunks.append({
                "document_id": doc_id,
                "section": section,
                "subsection": subsection,
                "chunk_id": f"{subsection}_{chunk_id}",
                "text": clean_text
            })


    return chunks


def process_file(filepath):
    filename = os.path.basename(filepath)
    doc_id = filename.replace("_clean.txt", "")

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    sections = split_into_sections(text)
    all_chunks = []

    for section_name, section_text in sections.items():
        if not section_text:
            continue

        # Special handling for DIRITTO
        if section_name in ["FATTO", "DIRITTO"]:
            points = split_into_points(section_text)
            for point_id, point_text in points:
                subsection = f"{section_name}_{point_id}"
                chunks = chunk_by_paragraph(
                    point_text, section_name, subsection, doc_id
                )
                all_chunks.extend(chunks)
        else:
            subsection = section_name
            chunks = chunk_by_paragraph(
                section_text, section_name, subsection, doc_id
            )
            all_chunks.extend(chunks)

    return all_chunks


def main():
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith("_clean.txt"):
            input_path = os.path.join(INPUT_DIR, filename)
            chunks = process_file(input_path)

            output_file = filename.replace("_clean.txt", "_chunks.json")
            output_path = os.path.join(OUTPUT_DIR, output_file)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(chunks, f, ensure_ascii=False, indent=2)

            print(f"Created {len(chunks)} chunks → {output_path}")


if __name__ == "__main__":
    main()
