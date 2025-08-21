import os

# Qdrant Cloud Configuration
# Use environment variables for production deployment (Cloud Run)
# Fall back to default values for local development

# Your Qdrant cloud URL
QDRANT_URL = os.getenv(
    "QDRANT_URL", 
    "https://416e0f86-bedc-4757-90e9-b3ee36e0775a.europe-west3-0.gcp.cloud.qdrant.io"
)

# Your Qdrant API key
QDRANT_API_KEY = os.getenv(
    "QDRANT_API_KEY", 
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.L7CqmGVrzbyLDh27EYddMKJonr3G3HXGGoHEPr2EmUQ"
)

# Collection name for products
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "products")
