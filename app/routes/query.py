from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from app.models.retrive import search_memory, ask_gemini

llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash', google_api_key='AIzaSyCO3C4hhry7CF8g18cwKPbQTrDpLqGd-Q8')
query_router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    id: str
    chats: list

@query_router.post("/")
async def post_query(data: QueryRequest):
    query = data.query
    id = data.id
    chat_history = data.chats
    print(data)
    if not id or not query:
        return {"messages": "Please upload pdf"}
    relevant_chunks = search_memory(question=query, k=3, id=id)
    if not relevant_chunks:
        return "No memory avaliable"
    response = ask_gemini(question=query, context_chunks=relevant_chunks, chat_history=chat_history)
    return {"response": response}

