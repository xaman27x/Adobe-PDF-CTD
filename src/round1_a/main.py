import json
from pathlib import Path
from src.common.pdf_parser import PDFParser
from src.round1_a.heading_detector import HeadingDetector

# Definition of directories. This will be changed as per the guidelines.
INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")

def process_document(pdf_path: Path) -> None:
    """
    Processes a single PDF document by parsing it
    and writes the output to a JSON file.
    """
    print(f"Processing {pdf_path.name}")

    try:
        # > Parse the PDF Document
        parsed_data = PDFParser.parse(str(pdf_path))
        if not parsed_data or not parsed_data.get("pages"):
            print(f"no content in {pdf_path.name}.")
            return

        # > Classifier/Detector instantiation
        detector = HeadingDetector(parsed_data["pages"])
        output_data = detector.classify()

        #  > Output is written to a JSON file
        output_filename = OUTPUT_DIR / f"{pdf_path.stem}.json"
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=4)
        print(f"wrote output to {output_filename.name}")
    
    except Exception as e:
        print(f"Exception in {pdf_path.name}: {e}")


def main():
    """
    Main function to run the heading extraction for all PDFs in the input directory.
    """
    INPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pdf_files = list(INPUT_DIR.glob("*.pdf"))
    if not pdf_files:
        return

    for pdf_file in pdf_files:
        process_document(pdf_file)


if __name__ == "__main__":
    main()