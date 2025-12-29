import os
from typing import List
from qdrant_client import QdrantClient
from fastembed import TextEmbedding
from dotenv import load_dotenv

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "humanoid_textbook")

# Initialize clients
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
model = TextEmbedding() # Defaults to BAAI/bge-small-en-v1.5

def get_relevant_context(query: str, limit: int = 5) -> str:
    if not QDRANT_URL:
        return "Warning: Vector database not configured."
    
    # Generate embedding
    query_vector = list(model.embed([query]))[0]
    
    # Search Qdrant
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=limit
    )
    
    # Combine results
    context_parts = []
    for res in results:
        content = res.payload.get("content", "")
        source = res.payload.get("source", "Unknown")
        context_parts.append(f"Source: {source}\nContent: {content}")
        
    return "\n\n---\n\n".join(context_parts)
