import requests
import fitz  # PyMuPDF
from io import BytesIO

def extract_text_from_pdf_url(pdf_url: str) -> str:
    """
    Downloads a PDF from a URL and extracts text from it.
    
    :param pdf_url: Direct link to the PDF file.
    :return: Extracted text from the PDF.
    """
    response = requests.get(pdf_url)
    
    if response.status_code != 200 or 'application/pdf' not in response.headers.get('Content-Type', ''):
        raise ValueError("URL did not return a valid PDF")

    pdf_data = BytesIO(response.content)
    text = ""

    with fitz.open(stream=pdf_data, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    
    return text
