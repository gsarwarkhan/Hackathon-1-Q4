import os
from qdrant_client import QdrantClient
import cohere
import numpy as np

# Assume API keys are set as environment variables
QDRANT_URL = "https://44f1eced-a617-4726-8d5d-90f66a56e2e2.us-east4-0.gcp.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.XLi_uw9vKDmaR7DK565IDF7Ryl5AxubOMhVO2Mi928U"
COHERE_API_KEY = "VaIaYh8GGZF3MGgjCC3y4zCGYt39tVyfi8bFDOmO" # User's Cohere API key

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
cohere_client = cohere.Client(api_key=COHERE_API_KEY)

# 1. Embed a fixed test query
test_query = "What is ROS 2?"
embed_response = cohere_client.embed(
    texts=[test_query],
    model='embed-english-v3.0',
    input_type='search_query'
)
question_embedding = embed_response.embeddings[0]

# Ensure embedding is a list of floats
if isinstance(question_embedding, np.ndarray):
    question_embedding_list = question_embedding.tolist()
else:
    question_embedding_list = question_embedding

# 2. Perform qdrant_client.search
search_results = client.query_points(
    collection_name="humanoid_textbook",
    query_vector=question_embedding_list,
    limit=1, # Just need one result to inspect payload
)

print(f"Search results count: {len(search_results)}")

if search_results:
    first_result = search_results[0]
    print("\n--- First Search Result Payload ---")
    print(first_result.payload)

    # Identify the correct payload key for context assembly
    print("\n--- Identifying Context Key ---")
    if "text" in first_result.payload:
        print("Payload contains a 'text' key. This is the likely key for context assembly.")
        print(f"Excerpt of 'text' payload: {first_result.payload['text'][:200]}...")
    elif "content" in first_result.payload:
        print("Payload contains a 'content' key. This could be the key for context assembly.")
        print(f"Excerpt of 'content' payload: {first_result.payload['content'][:200]}...")
    else:
        print("No common 'text' or 'content' key found in payload. Manual inspection needed.")
else:
    print("No search results found to verify payload structure.")
