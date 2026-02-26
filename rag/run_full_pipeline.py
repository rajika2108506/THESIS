import os
import shutil
import subprocess

RAW_DIR = "data/raw_pdfs"
WORK_DIR = "data/current_pdf"

TEXT_RAW_DIR = "data/text_raw"
TEXT_CLEAN_DIR = "data/text_clean"
CHUNKS_DIR = "data/chunks"
CHROMA_DIR = "chroma_db"
OUTPUT_DIR = "outputs"


# -------------------------------------------------
# Utility: Clear folder contents
# -------------------------------------------------
def clear_folder(folder_path):
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
            else:
                shutil.rmtree(file_path)


# -------------------------------------------------
# Run script safely
# -------------------------------------------------
def run_script(script_path):
    result = subprocess.run(["python", script_path])
    if result.returncode != 0:
        print(f"❌ Error running {script_path}")
        exit()


# -------------------------------------------------
# Main pipeline
# -------------------------------------------------
def main():

    pdf_files = [f for f in os.listdir(RAW_DIR) if f.endswith(".pdf")]

    for pdf in pdf_files:

        print("\n====================================")
        print(f"Processing: {pdf}")
        print("====================================")

        # 1️⃣ FULL CLEAN BEFORE PROCESSING
        clear_folder(WORK_DIR)
        clear_folder(TEXT_RAW_DIR)
        clear_folder(TEXT_CLEAN_DIR)
        clear_folder(CHUNKS_DIR)
        clear_folder(CHROMA_DIR)

        # 2️⃣ Copy ONE PDF to working folder
        shutil.copy(
            os.path.join(RAW_DIR, pdf),
            os.path.join(WORK_DIR, pdf)
        )

        # 3️⃣ Run full pipeline sequentially
        run_script("preprocessing/pdf_to_text.py")
        run_script("preprocessing/clean_text.py")
        run_script("chunking/chunk_text.py")
        run_script("vectorstore/ingest_chroma.py")
        run_script("rag/jsonex.py")

        print(f"✅ Completed: {pdf}")

    print("\n🎉 All documents processed successfully.")


if __name__ == "__main__":
    main()