import os
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
import cohere

# Configuration
QDRANT_URL = "https://44f1eced-a617-4726-8d5d-90f66a56e2e2.us-east4-0.gcp.cloud.qdrant.io"
QDRANT_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.XLi_uw9vKDmaR7DK565IDF7Ryl5AxubOMhVO2Mi928U"
COHERE_API_KEY = "VaIaYh8GGZF3MGgjCC3y4zCGYt39tVyfi8bFDOmO"
DOCS_PATH = os.path.join(os.path.dirname(__file__), '../../docs') # Path to your Docusaurus docs folder

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_KEY)
cohere_client_instance = cohere.Client(api_key=COHERE_API_KEY)

def prepare_collection():
    # Create collection if it doesn't exist
    client.recreate_collection(
        collection_name="humanoid_textbook",
        vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
    )

def ingest_docs():
    points = []
    idx = 1
    for root, dirs, files in os.walk(DOCS_PATH):
        for filename in files:
            if filename.endswith(".md") or filename.endswith(".mdx"):
                print(f"Processing file: {os.path.join(root, filename)}")
                with open(os.path.join(root, filename), 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Create vector embedding
                    embed_response = cohere_client_instance.embed(
                        texts=[content],
                        model='embed-english-v3.0',
                        input_type='search_document' # Or 'search_query' depending on usage, 'search_document' for ingestion
                    )
                    vector = embed_response.embeddings[0]
                    
                    points.append(PointStruct(
                        id=idx, 
                        vector=vector, 
                        payload={"text": content, "source": filename}
                    ))
                    idx += 1
    
    client.upsert(collection_name="humanoid_textbook", points=points)
    print(f"Successfully indexed {idx-1} documents.")

if __name__ == "__main__":
    prepare_collection()
    ingest_docs()