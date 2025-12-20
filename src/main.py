import os
import logging
from typing import List, Union, Dict, Any

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter # Kept for potential future use or if needed by QdrantClient internally
import cohere
import numpy as np # Used for potential np.ndarray to list conversion

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
# Ensure these environment variables are set
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

MAX_CONTEXT_LENGTH = 10000 # Maximum characters for context passed to LLM

# --- FastAPI App Initialization ---
app = FastAPI(
    title="RAG Chatbot API",
    description="A RAG-based chatbot using Cohere and Qdrant.",
    version="1.0.0",
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"], # Explicitly allow frontend origin
    allow_credentials=True, # Allow cookies/auth headers from this origin
    allow_methods=["GET", "POST", "OPTIONS"], # Explicitly allow methods needed, OPTIONS for preflight
    allow_headers=["Content-Type"], # Explicitly allow Content-Type header
)

# --- Service Clients Initialization ---
qdrant_client_instance: QdrantClient = None
cohere_client_instance: cohere.Client = None

@app.on_event("startup")
async def startup_event():
    global qdrant_client_instance, cohere_client_instance

    try:
        if not QDRANT_URL or not QDRANT_API_KEY:
            raise ValueError("QDRANT_URL and QDRANT_API_KEY environment variables must be set.")
        qdrant_client_instance = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        logger.info("Qdrant client initialized successfully.")

        if not COHERE_API_KEY:
            raise ValueError("COHERE_API_KEY environment variable must be set.")
        cohere_client_instance = cohere.Client(api_key=COHERE_API_KEY)
        logger.info("Cohere client initialized successfully.")
        
    except Exception as e:
        logger.error(f"Failed to initialize service clients on startup: {e}", exc_info=True)
        raise

# --- Pydantic Models ---
class AskRequest(BaseModel):
    question: str
    user_context: str = ""

class AskResponse(BaseModel):
    answer: str

# --- Health Check Endpoint ---
@app.get("/", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint to test if the server is alive.
    """
    logger.info("Health check endpoint hit.")
    return {"status": "alive", "message": "RAG Chatbot API is running!"}

# --- FINAL ROBUST RAG PIPELINE HANDLER ---
@app.post("/ask", response_model=AskResponse)
async def ask_chatbot(request: AskRequest):
    """
    Handles a user's question by performing Retrieval-Augmented Generation.
    1.  Generates an embedding for the user's question using Cohere.
    2.  Searches Qdrant for the most relevant context using the embedding.
    3.  Assembles and truncates context from Qdrant results.
    4.  Generates an answer using Cohere command-r.
    """
    if not request.question:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Question cannot be empty.")

    try:
        # 1. Generate query embedding using Cohere
        if cohere_client_instance is None:
            raise RuntimeError("Cohere client not initialized.")
            
        embed_response = cohere_client_instance.embed(
            texts=[request.question],
            model='embed-english-v3.0',
            input_type='search_query' # Crucial for query-time embeddings as per spec
        )
        question_embedding = embed_response.embeddings[0] # This should be List[float]
        logger.info("Cohere embedding generated successfully.") # Debug log
        
    except Exception as e:
        logger.error(f"Cohere API (embedding) failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate embedding with Cohere: {e}"
        )

    try:
        # 2. Perform Qdrant vector search
        if qdrant_client_instance is None:
            raise RuntimeError("Qdrant client not initialized.")
            
        # Ensure question_embedding is a list of floats, as required by qdrant_client.search
        if isinstance(question_embedding, np.ndarray):
            question_embedding_list = question_embedding.tolist()
        else:
            question_embedding_list = question_embedding
        
        search_results = qdrant_client_instance.query_points(
            collection_name="humanoid_textbook",
            query=question_embedding_list, # Pass the Cohere embedding directly to 'query'
            limit=3,
        )
        logger.info(f"Qdrant search returned {len(search_results)} results.") # Debug log
        
        # Defensive handling: Empty Qdrant results
        if not search_results:
            logger.warning("Qdrant search returned no relevant documents for the query.")
            return {"answer": "I couldn't find any relevant information in the textbook to answer your question. Please try rephrasing or ask a different question."}

        # 3. Safely assemble context from payload
        assembled_context_parts = []
        for res in search_results:
            # Defensive handling: Missing payload text field
            text_content = res.payload.get('text', '')
            if text_content: # Only add if text content is not empty
                assembled_context_parts.append(f"--- Context Snippet from: {res.payload.get('source', 'Unknown')} ---\n{text_content}")
            else:
                logger.warning(f"Qdrant result {res.id} missing 'text' in payload or text is empty.")
        
        context = "\n\n".join(assembled_context_parts)
        
        # Defensive handling: Truncate context to a safe size
        if len(context) > MAX_CONTEXT_LENGTH:
            logger.warning(f"Context truncated from {len(context)} to {MAX_CONTEXT_LENGTH} characters before sending to LLM.")
            context = context[:MAX_CONTEXT_LENGTH]
        elif not context: # If after assembly and potential truncation, context is still empty
            logger.warning("Assembled context is empty after Qdrant search.")
            return {"answer": "I found some documents, but couldn't extract useful context to answer your question. Please try rephrasing."}

        logger.debug(f"Assembled context: {context[:500]}...") # Log first 500 chars of context
        
    except Exception as e:
        logger.error(f"Qdrant retrieval or context assembly failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve context from Qdrant: {e}"
        )

    try:
        # 4. Generate an answer using Cohere command-r
        if cohere_client_instance is None:
            raise RuntimeError("Cohere client not initialized.")

        prompt = f"""
        You are an expert AI tutor for a course on Physical AI and Humanoid Robotics.
A student has asked a question. Use the following context from the course textbook to provide a clear,
professional, and helpful answer. Ensure your answer is directly relevant to the question and the provided context.

**Student Background (if provided):**
{request.user_context if request.user_context else "N/A"}

**Context from the textbook:**
{context if context else "No relevant context found in the textbook."} 

**Student's Question:**
{request.question}

**Answer:**
"""
        
        chat_response = cohere_client_instance.chat(
            model='command-r', # Optimized for RAG and instruction following
            message=prompt
        )
        
        # Defensive handling: Empty or truncated Cohere generation
        if not chat_response.text:
            logger.warning("Cohere generation returned an empty response.")
            return {"answer": "I received an empty response from the AI. Please try again or ask a different question."}

        logger.info("Cohere answer generated successfully.") # Debug log
        
        return {"answer": chat_response.text}

    except Exception as e:
        logger.error(f"Cohere API (generation) failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate answer: {e}"
        )

# --- Uvicorn Runner ---
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server with Uvicorn...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
