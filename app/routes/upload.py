from fastapi import APIRouter, UploadFile, File
import fitz
from uuid import uuid4
from io import BytesIO
#local file
from app.models.pinecone_db import upsert_large_document

upload_router = APIRouter()

@upload_router.post("/pdf")
async def extract_text(file: UploadFile = File(...)):
    # Create a temporary unique filename
    id = str(uuid4())
    file_bytes = await file.read()
    text = extract_text_pdf(file_bytes=file_bytes)

    data = await upsert_large_document(text=text, index_name=id)
    return id

def extract_text_pdf(file_bytes: bytes):
    text = ""
    with fitz.open(stream=BytesIO(file_bytes), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text
