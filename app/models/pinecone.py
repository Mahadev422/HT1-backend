# Import the Pinecone library
from pinecone import Pinecone

# Initialize a Pinecone client with your API key
pc = Pinecone(api_key="{{YOUR_API_KEY}}")

# Create a dense index with integrated embedding
index_name = "quickstart-py"
if not pc.has_index(index_name):
    pc.create_index_for_model(
        name=index_name,
        cloud="aws",
        region="us-east-1",
        embed={
            "model":"llama-text-embed-v2",
            "field_map":{"text": "chunk_text"}
        }
    )

async def create_index(index_name: str, docs):
    pc.create_index_for_model(
        name=index_name,
        cloud="aws",
        region="us-east-1",
        embed={
            "model":"llama-text-embed-v2",
            "field_map":{"text": "chunk_text"}
        }
    )

async def upload_to_pinecone(index_name: str):
    dense_index = pc.Index(index_name)
    dense_index.upsert_records(f"{index_name}-records", )
    