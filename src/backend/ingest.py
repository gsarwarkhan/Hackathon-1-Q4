"""
This script handles the ingestion of documentation into the Qdrant vector database.
It processes markdown files, splits them into chunks, generates vector embeddings
using an OpenRouter model, and upserts them into a Qdrant collection.

This script must be run once to populate the vector database.
"""
import os
import logging
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models
from openai import OpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- Configuration ---
# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Environment Variables
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
# We use text-embedding-3-small as a default, it has a dimension of 1536
EMBEDDING_MODEL = os.getenv("OPENROUTER_EMBEDDING_MODEL", "openai/text-embedding-3-small")
EMBEDDING_DIMENSION = 1536

# Qdrant and Document Path Configuration
COLLECTION_NAME = "humanoid_textbook"
DOCS_PATH = os.path.join(os.path.dirname(__file__), '../../docs')

def validate_env_vars():
    """Ensure all required environment variables are set."""
    required_vars = ["QDRANT_URL", "QDRANT_API_KEY", "OPENROUTER_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        message = f"Missing required environment variables: {', '.join(missing_vars)}"
        logger.error(message)
        raise ValueError(message)
    logger.info("Environment variables validated successfully.")

def get_clients():
    """Initialize and return Qdrant and OpenAI clients."""
    qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    openai_client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL,
    )
    logger.info("Qdrant and OpenAI clients initialized.")
    return qdrant_client, openai_client

def prepare_collection(qdrant_client: QdrantClient):
    """Create or recreate the Qdrant collection with the correct vector parameters."""
    try:
        qdrant_client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=EMBEDDING_DIMENSION, distance=models.Distance.COSINE),
        )
        logger.info(f"Collection '{COLLECTION_NAME}' created or recreated successfully.")
    except Exception as e:
        logger.error(f"Failed to create collection: {e}")
        raise

def ingest_docs(qdrant_client: QdrantClient, openai_client: OpenAI):
    """
    Walks through the docs directory, splits markdown files, generates embeddings,
    and upserts the data into Qdrant.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )

    points = []
    point_id = 0
    for root, _, files in os.walk(DOCS_PATH):
        for filename in files:
            if filename.endswith((".md", ".mdx")):
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    chunks = text_splitter.split_text(content)
                    logger.info(f"Processing {len(chunks)} chunks from: {file_path}")

                    # Generate embeddings for all chunks in the file at once
                    if chunks:
                        embed_response = openai_client.embeddings.create(
                            model=EMBEDDING_MODEL,
                            input=chunks
                        )
                        
                        for i, chunk in enumerate(chunks):
                            vector = embed_response.data[i].embedding
                            
                            points.append(models.PointStruct(
                                id=point_id, 
                                vector=vector, 
                                payload={"text": chunk, "source": filename}
                            ))
                            point_id += 1
                
                except Exception as e:
                    logger.error(f"Failed to process file {file_path}: {e}")

    if points:
        logger.info(f"Starting to upsert {len(points)} points to Qdrant...")
        # Upsert points in batches to avoid overwhelming the service
        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
            wait=True  # Wait for the operation to complete
        )
        logger.info(f"Successfully indexed {len(points)} chunks.")
    else:
        logger.warning("No documents found to index.")


if __name__ == "__main__":
    logger.info("Starting ingestion process...")
    validate_env_vars()
    qdrant, openai = get_clients()
    prepare_collection(qdrant)
    ingest_docs(qdrant, openai)
    logger.info("Ingestion process finished.")
