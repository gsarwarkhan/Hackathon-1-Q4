import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance

# Assume API keys are set as environment variables
QDRANT_URL = "https://44f1eced-a617-4726-8d5d-90f66a56e2e2.us-east4-0.gcp.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.XLi_uw9vKDmaR7DK565IDF7Ryl5AxubOMhVO2Mi928U"

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# Get collection information
collection_info = client.get_collection("humanoid_textbook")

# Correctly access collection details
print(f"Collection Status: {collection_info.status.value}") # .value to get string representation
print(f"Collection Vectors Config: {collection_info.config.params.vectors}")

# Interpret the output
print("\n--- Interpretation ---")
if collection_info.config.params.vectors.size == 1024:
    print("Vector size matches Cohere embed-english-v3.0 (1024).")
else:
    print(f"WARNING: Vector size ({collection_info.config.params.vectors.size}) does NOT match Cohere embed-english-v3.0 (expected 1024).")

if collection_info.config.params.vectors.distance == Distance.COSINE:
    print("Distance metric is COSINE, which is standard for embeddings.")
else:
    print(f"WARNING: Distance metric ({collection_info.config.params.vectors.distance}) does NOT match COSINE.")