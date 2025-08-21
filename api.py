from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer, util
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models
import uuid

app = FastAPI(title="Product Recommendation API")

# Load the sentence transformer model
print("Loading sentence transformer model...")
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✓ Model loaded successfully")
except Exception as e:
    print(f"✗ Failed to load model: {e}")
    raise

# Import configuration for Qdrant cloud
from config import QDRANT_URL, QDRANT_API_KEY, COLLECTION_NAME

# Connect to Qdrant cloud
print("Connecting to Qdrant cloud...")
try:
    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
    )
    print("✓ Connected to Qdrant cloud")
except Exception as e:
    print(f"✗ Failed to connect to Qdrant: {e}")
    raise

# We're now importing COLLECTION_NAME from config.py

# Create collection if it doesn't exist
try:
    client.get_collection(COLLECTION_NAME)
    print(f"Collection '{COLLECTION_NAME}' already exists")
except Exception as e:
    print(f"Collection '{COLLECTION_NAME}' doesn't exist, creating it...")
    try:
        # Create a new collection for products
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=model.get_sentence_embedding_dimension(),  # Dimension from the model
                distance=models.Distance.COSINE,
            )
        )
        print(f"Successfully created collection '{COLLECTION_NAME}'")
    except Exception as create_error:
        print(f"Failed to create collection: {create_error}")
        # Continue anyway - we'll handle errors in individual endpoints

# Define data models
class Product(BaseModel):
    name: str
    desc: str
    price: float

class RecommendationRequest(BaseModel):
    query: str
    target_price: float
    num_results: int = 3
    alpha: float = 0.7  # Weight for text similarity
    beta: float = 0.3   # Weight for price similarity

class RecommendationResponse(BaseModel):
    recommendations: List[Dict[str, Any]]

@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run"""
    return {"status": "healthy", "service": "recommendation-api"}

@app.post("/products/", status_code=201)
async def add_product(product: Product):
    """
    Add a product to the Qdrant database
    """
    # Generate a unique ID for the product
    product_id = str(uuid.uuid4())
    
    # Create the product text and encode it
    product_text = f"{product.name} - {product.desc}"
    product_embedding = model.encode(product_text)
    
    # Store the product in Qdrant
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            models.PointStruct(
                id=product_id,
                vector=product_embedding.tolist(),
                payload={
                    "name": product.name,
                    "desc": product.desc,
                    "price": product.price,
                    "text": product_text
                }
            )
        ]
    )
    
    return {"id": product_id, "message": "Product added successfully"}

@app.post("/recommendations/", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Get product recommendations based on query and price preference
    """
    # Encode the user query
    user_embedding = model.encode(request.query)
    
    # Search for similar products in Qdrant
    search_result = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=user_embedding.tolist(),
        limit=100  # Get more results than needed for price filtering
    )
    
    # If no results, return empty
    if not search_result:
        return {"recommendations": []}
    
    # Extract products and calculate combined score with price similarity
    recommendations = []
    max_price = max([hit.payload.get("price", 0) for hit in search_result])
    
    if max_price == 0:
        max_price = 1  # Avoid division by zero
    
    normalized_target_price = request.target_price / max_price
    
    for hit in search_result:
        product = hit.payload
        text_similarity = hit.score
        
        # Calculate price similarity
        normalized_price = product.get("price", 0) / max_price
        price_similarity = 1 - abs(normalized_price - normalized_target_price)
        
        # Calculate final score
        final_score = request.alpha * text_similarity + request.beta * price_similarity
        
        recommendations.append({
            "id": hit.id,
            "name": product.get("name"),
            "price": product.get("price"),
            "description": product.get("desc"),
            "score": final_score
        })
    
    # Sort by final score and take top results
    recommendations.sort(key=lambda x: x["score"], reverse=True)
    recommendations = recommendations[:request.num_results]
    
    return {"recommendations": recommendations}

@app.get("/products/", status_code=200)
async def list_products():
    """
    List all products in the database
    """
    # Scroll through all products in the collection
    scroll_result = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=100,  # Adjust as needed
        with_payload=True,
        with_vectors=False
    )
    
    products = []
    for point in scroll_result[0]:
        products.append({
            "id": point.id,
            "name": point.payload.get("name"),
            "price": point.payload.get("price"),
            "description": point.payload.get("desc")
        })
    
    return {"products": products}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
