from google import genai
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer
from pinecone import Pinecone
from uuid import uuid4

pc = Pinecone(api_key="pcsk_44QeqV_EjKjUQrsM7r1WB94xYLE9MQdivSU4kVa19CsqPRj3yjSttKvF4oBbFnxKGFCZNw")
model = SentenceTransformer("BAAI/bge-large-en")

client = genai.Client(api_key="AIzaSyDWdWOBveuDAQaPdT8Bdcx0yWpHAkAbm08")
from google.genai.types import GenerateContentConfig

async def create_index(index_name: str):
  if pc.has_index(index_name):
     return True
  pc.create_index_for_model(
        name=index_name,
        cloud="aws",
        region="us-east-1",
        embed={
            "model":"llama-text-embed-v2",
            "field_map":{"text": "chunk_text"}
        }
    )
  return True
  
history = []

async def gemini(query: str, context):
  chat = client.chats.create(
    model='gemini-2.5-flash', 
    config=GenerateContentConfig(
      system_instruction='''
        You are an AI assisstant for helping people to give correct answer based on the given context.
        If answer is not present in the context then you try to give short answer on your own knowledge.
        Use the context below to answer the question in very concise and simple language (max 30 words).
      ''',
      temperature=0.7
    )
    )
  prompt = (
        f"""
        Context:\n{''.join(context)}
        Question: {query}"""
    )
  
  res = chat.send_message(prompt)
  
  history.append({"role": "user", "text": query})
  history.append({"role": "model", "text": res.text})
  return res.text

tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-large-en")


def embed_for_pinecone(text: str):
    chunks = chunk_by_tokens(text)
    embeddings = model.encode(chunks).tolist()

    vectors = []
    for i, embedding in enumerate(embeddings):
        vectors.append({
            "id": str(uuid4()),
            "values": embedding,  # 1024-dimensional vector
            "metadata": {
                "chunk_text": chunks[i],
                "chunk_index": i
            }
        })
    return vectors

def chunk_by_tokens(text: str):
    # Tokenize the text into token IDs
    max_tokens = 400
    stride=32
    input_ids = tokenizer.encode(text, add_special_tokens=False)
    
    if len(input_ids) <= max_tokens:
        # No need to chunk
        return [text]

    chunks = []
    start = 0
    while start < len(input_ids):
        end = min(start + max_tokens, len(input_ids))
        chunk_ids = input_ids[start:end]
        chunk_text = tokenizer.decode(chunk_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)
        chunks.append(chunk_text.strip())
        if end == len(input_ids):
            break
        start += max_tokens - stride  # Move with overlap

    return chunks

async def gemini_embedding(query: str):
  response = client.models.embed_content(
    model="gemini-embedding-001",
    contents=query,
    config={
          'output_dimensionality': 1024
      },
  )
  return response.embeddings[0].values

async def upsert_large_document(text: str, index_name: str, metadata: dict = {}):
    
    status = await create_index(index_name=index_name)
    if not status:
       return
    vectors = embed_for_pinecone(text=text)

    index = pc.Index(index_name)
    index.upsert(vectors=vectors, namespace='hackrx')

    return {"status": True}

async def search_query_from_index(query: str, index_name: str):
    query_embedding = await gemini_embedding(query=query)
    index = pc.Index(index_name)

    response = index.query(
        namespace="hackrx",
        vector=query_embedding,
        top_k=3,
        include_metadata=True,
    )

    results = []
    for match in response['matches']:
        results.append(
            match["metadata"].get("chunk", "No text found")
        )

    res = await gemini(query=query, context=results)

    return res