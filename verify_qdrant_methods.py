import os
import qdrant_client
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance
import inspect

# Assume API keys are set as environment variables (or hardcode for this test)
QDRANT_URL = "https://44f1eced-a617-4726-8d5d-90f66a56e2e2.us-east4-0.gcp.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.XLi_uw9vKDmaR7DK565IDF7Ryl5AxubOMhVO2Mi928U"

if not QDRANT_URL or not QDRANT_API_KEY:
    raise ValueError("QDRANT_URL and QDRANT_API_KEY must be set.")

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)



print("\n--- Available methods on QdrantClient instance ---")
# List methods that are not special dunder methods
available_methods = [
    attr for attr in dir(client) if not attr.startswith('__') and callable(getattr(client, attr))
]
available_methods.sort()
for method_name in available_methods:
    print(method_name)

print("\n--- Inspecting 'search_points' method (if available) ---")
if hasattr(client, 'search_points'):
    print(inspect.signature(client.search_points))
else:
    print("'search_points' method not found.")

print("\n--- Inspecting 'query_points' method (if available) ---")
if hasattr(client, 'query_points'):
    print(inspect.signature(client.query_points))
else:
    print("'query_points' method not found.")

print("\n--- Inspecting 'search' method (if available) ---")
if hasattr(client, 'search'):
    print(inspect.signature(client.search))
else:
    print("'search' method not found.")
