from fastapi import APIRouter, UploadFile, File
import os, json, shutil
import faiss, fitz
from uuid import uuid4
#local file
from app.models.pdf_upload import chunk_text, embed_chunks, pdf_text_extract


UPLOAD_DIR = "data"
os.makedirs(UPLOAD_DIR, exist_ok=True)

upload_router = APIRouter()

@upload_router.post("/pdf")
async def extract_text(file: UploadFile = File(...)):
    # Create a temporary unique filename
    id = uuid4()
    temp_filename = f"{id}.pdf"
    text = pdf_text_extract(temp_filename=temp_filename, file=file)
    chunks = chunk_text(text=text)
    vectors = embed_chunks(chunks=chunks)
    index = faiss.IndexFlatL2(384)
    index.add(vectors)
    
    INDEX_FILE = os.path.join(UPLOAD_DIR, f"faiss/{id}.faiss")
    META_FILE = os.path.join(UPLOAD_DIR, f"json/{id}.json")
    faiss.write_index(index, INDEX_FILE)
    with open(META_FILE, "w") as f:
        json.dump({"chunks": chunks}, f)

    return {"id": id, "message": "Uploaded Successfully"}

