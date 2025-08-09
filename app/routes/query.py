from fastapi import APIRouter
from pydantic import BaseModel
from app.models.pinecone_db import search_query_from_index

query_router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    id: str

@query_router.post("/")
async def post_query(data: QueryRequest):
    query = data.query
    id = data.id
    response = await search_query_from_index(query=query, index_name=id)

    return {"answers": response}
