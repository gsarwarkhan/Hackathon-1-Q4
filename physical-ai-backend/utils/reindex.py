import os
import glob
from qdrant_client import QdrantClient
from qdrant_client.http import models
from fastembed import TextEmbedding
from dotenv import load_dotenv

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "humanoid_textbook")

# Initialize
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
model = TextEmbedding()

def reindex():
    print(f"Re-indexing docs to {COLLECTION_NAME} at {QDRANT_URL}...")
    
    # 1. Re-create collection
    try:
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
        )
    except Exception as e:
        print(f"Error creating collection: {e}")
        return

    # 2. Find markdown files
    # assuming this is run from the root of backend or utils
    docs_path = os.path.join(os.path.dirname(__file__), "..", "..", "docs")
    if not os.path.exists(docs_path):
        docs_path = os.path.join(os.path.dirname(__file__), "..", "docs") # alternative
        
    md_files = glob.glob(os.path.join(docs_path, "**", "*.md"), recursive=True)
    
    documents = []
    metadata = []
    ids = []
    
    count = 0
    for file_path in md_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Simple chunking by paragraph (can be improved)
            chunks = content.split("\n\n")
            for i, chunk in enumerate(chunks):
                if len(chunk.strip()) < 50: continue
                
                documents.append(chunk)
                metadata.append({
                    "content": chunk,
                    "source": os.path.basename(file_path),
                    "chunk_id": i
                })
                ids.append(count)
                count += 1

    print(f"Found {len(md_files)} files, resulting in {len(documents)} chunks.")

    # 3. Embed and Upload
    embeddings = list(model.embed(documents))
    
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=models.Batch(
            ids=ids,
            vectors=embeddings,
            payloads=metadata
        )
    )
    
    print("Successfully indexed!")

if __name__ == "__main__":
    reindex()
