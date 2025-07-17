import os
import json
from datetime import datetime

from src.round1_a.heading_extractor import extract_headings_from_pdf

def process_pdf(input_path: str, output_path: str) -> bool:
    try:
        title, outline = extract_headings_from_pdf(input_path)
        output = {
            "title": title,
            "outline": outline,
            "processed_at": datetime.utcnow().isoformat() + "Z"
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        return True

    except Exception as e:
        print(f"Error processing {input_path}: {str(e)}")
        return False

def main():
    input_dir = "input"
    output_dir = "output"

    if not os.path.exists(input_dir):
        print(f"❌ Input directory '{input_dir}' does not exist.")
        return

    os.makedirs(output_dir, exist_ok=True)

    processed = 0
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.json")

            if process_pdf(input_path, output_path):
                processed += 1
                print(f"✅ Processed {filename}")

    print(f"\n🎉 Completed. Processed {processed} file(s).")

if __name__ == "__main__":
    main()
