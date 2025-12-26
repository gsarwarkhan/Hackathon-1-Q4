import os
from qdrant_client import QdrantClient

def main():
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")

    print("QDRANT_URL:", qdrant_url)
    print("QDRANT_API_KEY present:", bool(qdrant_api_key))

    if not qdrant_url or not qdrant_api_key:
        raise RuntimeError("Missing QDRANT_URL or QDRANT_API_KEY environment variable")

    client = QdrantClient(
        url=qdrant_url,
        api_key=qdrant_api_key,
        check_compatibility=False
    )

    collections = client.get_collections()
    print("Collections:")
    print(collections)

if __name__ == "__main__":
    main()
