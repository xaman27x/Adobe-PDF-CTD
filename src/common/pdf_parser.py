import fitz
from typing import List, Dict, Any

class PDFParser:
    """
    A high-performance PDF parser using PyMuPDF (fitz) to extract
    structured text data, including layout and font information.
    """

    @staticmethod
    def parse(pdf_path: str) -> Dict[str, Any]:
        """
        Parses a PDF file and extracts structured text data for each page.

        Args:
            pdf_path: The file path to the PDF document.

        Returns:
            A dictionary containing document metadata and a list of page data.
            Each page's data is a structured dictionary from get_text("dict").
        """
        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            print(f"Error opening or parsing {pdf_path}: {e}")
            return {"pages": [], "metadata": {}}

        document_data = {
            "page_count": doc.page_count,
            "metadata": doc.metadata,
            "pages": []
        }

        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            page_data = page.get_text("dict", sort=True)
            document_data["pages"].append(page_data)

        doc.close()
        return document_data
