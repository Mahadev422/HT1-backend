from fastapi import APIRouter, UploadFile, File, HTTPException
import os
from uuid import uuid4
import asyncio

UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()

@router.post("/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    filename = f"{uuid4()}.pdf"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    await asyncio.sleep(5)
    return {"filename": filename, "message": "Upload successful"}
