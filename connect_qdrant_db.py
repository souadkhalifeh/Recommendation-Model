import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client.models import PayloadSchemaType, CollectionStatus

load_dotenv() 

try:
    QDRANT_API_KEY = os.environ['QDRANT_API_KEY']
    print("QDRANT_API_KEY is set.")
except KeyError:
    print("QDRANT_API_KEY is not set. Please check your .env file.")
    raise KeyError("QDRANT_API_KEY must be set in the .env file.")
    
    
client = QdrantClient(
    url="https://69814424-871c-4965-b522-59c83512349d.europe-west3-0.gcp.cloud.qdrant.io:6333",
    api_key=QDRANT_API_KEY,
)

print(client.get_collections())    

COLLECTION_NAME = "swap-embeddings"

if not client.collection_exists(COLLECTION_NAME):
    print(f"Collection '{COLLECTION_NAME}' does not exist. Creating it.")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )
else:
    print(f"Collection '{COLLECTION_NAME}' already exists. Using the existing collection.")