from config import QDRANT_URL, QDRANT_API_KEY, COLLECTION_NAME
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer

print("Testing Qdrant connection...")
QDRANT_URL = "https://416e0f86-bedc-4757-90e9-b3ee36e0775a.europe-west3-0.gcp.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.L7CqmGVrzbyLDh27EYddMKJonr3G3HXGGoHEPr2EmUQ"

try:
    # Test connection to Qdrant cloud
    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
    )
    print("✓ Successfully connected to Qdrant cloud")
    
    # Test if we can get collection info
    try:
        collection_info = client.get_collection(COLLECTION_NAME)
        print(f"✓ Collection '{COLLECTION_NAME}' exists")
        print(f"  - Vectors count: {collection_info.vectors_count}")
        print(f"  - Points count: {collection_info.points_count}")
    except Exception as e:
        print(f"⚠ Collection '{COLLECTION_NAME}' doesn't exist: {e}")
        
        # Try to create the collection
        try:
            model = SentenceTransformer('all-MiniLM-L6-v2')
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=model.get_sentence_embedding_dimension(),
                    distance=models.Distance.COSINE,
                )
            )
            print(f"✓ Created collection '{COLLECTION_NAME}'")
        except Exception as create_error:
            print(f"✗ Failed to create collection: {create_error}")
    
    # Test basic operations
    try:
        collections = client.get_collections()
        print(f"✓ Available collections: {[c.name for c in collections.collections]}")
    except Exception as e:
        print(f"✗ Failed to list collections: {e}")
        
except Exception as e:
    print(f"✗ Failed to connect to Qdrant: {e}")
    print("Please check your QDRANT_URL and QDRANT_API_KEY in config.py")
