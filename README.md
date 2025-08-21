# Product Recommendation API

This API provides product recommendations based on text similarity and price preferences using sentence transformers and Qdrant vector database.

## Features

- Store product information in Qdrant cloud vector database
- Get personalized product recommendations based on text query and price preferences
- List all products in the database

## Setup

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

2. Configure your Qdrant cloud credentials:
   - Open `config.py`
   - Replace the placeholder values with your actual Qdrant cloud URL and API key
   ```python
   QDRANT_URL = "https://your-qdrant-cluster-url.qdrant.io"
   QDRANT_API_KEY = "your-api-key-here"
   ```

3. Start the API server:
   ```
   uvicorn api:app --reload
   ```

## API Endpoints

### Add a Product

```
POST /products/
```

Request body:
```json
{
  "name": "Product Name",
  "desc": "Product Description",
  "price": 99.99
}
```

### List All Products

```
GET /products/
```

### Get Recommendations

```
POST /recommendations/
```

Request body:
```json
{
  "query": "Search query text",
  "target_price": 100.0,
  "num_results": 3,
  "alpha": 0.7,
  "beta": 0.3
}
```

## Testing

You can test the API using the provided `test_api.py` script:

```
python test_api.py
```

This will add sample products to the database and test the recommendation functionality.

## How It Works

1. Products are stored in Qdrant with vector embeddings generated from their name and description
2. When a user makes a recommendation request, their query is converted to a vector embedding
3. The API finds products with similar embeddings and adjusts scores based on price preferences
4. Results are returned sorted by relevance
