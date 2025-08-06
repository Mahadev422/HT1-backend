from fastapi import FastAPI
from app.routes.upload import upload_router
from app.routes.query import query_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
   "http://localhost:5173"
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
  return {"message": "Successfully"}

app.include_router(router=upload_router, prefix='/upload', tags=['upload'])
app.include_router(router=query_router, prefix='/query', tags=['query'])