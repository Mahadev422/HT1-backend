from fastapi import FastAPI
from app.routes.upload import upload_router
from app.routes.query import query_router
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uuid import uuid4
#local function
from app.models.helpers import extract_text_from_pdf_url
from app.models.pinecone_db import upsert_large_document, search_query_from_index

app = FastAPI()

origins = [
   "http://localhost:5173"
   "https://ht-1-rho.vercel.app/"
]

app.add_middleware(
   CORSMiddleware, 
   allow_origins=origins,
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"]
)

@app.get('/')
def hello():
  return {"message": "Success"}

class hackrxRequest(BaseModel):
  documents: str
  questions: list[str]

@app.post('/hackrx/run')
async def hackrx(data: hackrxRequest):
  index_name = 'hackrx'
  questions = data.questions
  text = extract_text_from_pdf_url(pdf_url=data.documents)
  data = await upsert_large_document(text=text, index_name=index_name)
  print('2')
  
  if not data:
    return {"message": "failed to save pdf"}
  
  answers = []
  for question in questions:
    response = await search_query_from_index(query=question, index_name=index_name)
    answers.append(response)
  return {"answers": answers}

app.include_router(router=upload_router, prefix='/upload', tags=['upload'])
app.include_router(router=query_router, prefix='/query', tags=['query'])