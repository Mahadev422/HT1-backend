import os, shutil, asyncio
import fitz
from fastapi import UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from langchain_google_genai import ChatGoogleGenerativeAI
from sentence_transformers import SentenceTransformer


DATA_FOLDER = "data"
MEMORY_FOLDER = "memory_store"
os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(MEMORY_FOLDER, exist_ok=True)

EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
VECTOR_DIM = 384  # for this model

# === FUNCTIONS ===

def chunk_text(text, chunk_size=500):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def embed_chunks(chunks):
    return EMBED_MODEL.encode(chunks)


def pdf_text_extract(temp_filename: str, file: UploadFile = File(...)):

    try:
    # Save uploaded PDF to disk
        file_path = f"uploaded_pdfs/{temp_filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        text = ""
        with fitz.open(filename=file_path) as doc:
            for page in doc:
                text += page.get_text()

        return text.strip()

    except Exception as e:
        # Raise an exception, not return a response
        raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")
    
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)