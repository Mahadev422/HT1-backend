from fastapi import FastAPI
from app.routes.upload import router
from pydantic import BaseModel
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

app.include_router(router=router, prefix='/upload', tags=['upload'])

class QueryRequest(BaseModel):
    query: str

@app.post("/query")
async def post_query(data: QueryRequest):
    return {"response": "Success"}
