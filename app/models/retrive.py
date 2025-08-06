import os
import faiss
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from sentence_transformers import SentenceTransformer
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate

# === CONFIG ===
GOOGLE_API_KEY = "AIzaSyCO3C4hhry7CF8g18cwKPbQTrDpLqGd-Q8"
genai = ChatGoogleGenerativeAI(google_api_key=GOOGLE_API_KEY, model='gemini-2.5-flash', temperature=0.7)

DATA_FOLDER = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)

EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")


def load_index_and_metadata(id: str):
  
  INDEX_FILE = os.path.join(DATA_FOLDER, f"faiss/{id}.faiss")
  META_FILE = os.path.join(DATA_FOLDER, f"json/{id}.json")

  if not os.path.exists(INDEX_FILE) or not os.path.exists(META_FILE):
      print("❌ No memory found. Please summarize a file first.")
      return None, None
  index = faiss.read_index(INDEX_FILE)
  with open(META_FILE, "r") as f:
      chunks = json.load(f)["chunks"]
  return index, chunks

def search_memory(question: str, k: int, id: str):
    
    index, chunks = load_index_and_metadata(id)
    if index is None:
        return []

    q_vector = EMBED_MODEL.encode([question])
    _, I = index.search(q_vector, k)
    return [chunks[i] for i in I[0]]

from langchain.schema import HumanMessage, AIMessage

def convert_to_langchain_messages(messages: list):
    converted = []
    for msg in messages:
        text = msg.text
        role = msg.role

        if role == "user":
            converted.append(HumanMessage(content=text))
        elif role == "bot":
            converted.append(AIMessage(content=text))
        else:
            raise ValueError(f"Unknown sender type: {role}")

    return converted
  

def ask_gemini(question: str, context_chunks, chat_history: list):

    # prompt = ChatPromptTemplate([
    #     SystemMessage('''
    #     You are an AI assistant for question-answering tasks and friendly messages. Use the following pieces of retrieved context to answer the question.
    #     If you don't know the answer based on the context, then answer it by yourself.
    #     Use three sentences maximum and keep the answer concise.
        
    #     Question: {question}
    #     Context: {context_chunks}
    # '''),

    # ])
    prompt = f'''
        You are an AI assistant for question-answering tasks and friendly messages. Use the following pieces of retrieved context to answer the question.
        If you don't know the answer based on the context, then answer it by yourself.
        Use three sentences maximum and keep the answer concise.
        
        Question: {question}
        Context: {context_chunks}
    '''
    p = ChatPromptTemplate.from_template(prompt)
    #messages = convert_to_langchain_messages(messages=chat_history)
    #genai(messages=messages)
    response = genai.invoke(prompt).content
    return response


