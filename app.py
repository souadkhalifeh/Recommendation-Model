import os
import logging
from flask import Flask, request, jsonify
import torch
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForTokenClassification
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import re
from connect_qdrant_db import client, COLLECTION_NAME
from qdrant_client.models import PointStruct, PayloadSchemaType, Filter, FieldCondition, Range, MatchValue
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from tqdm import tqdm
import uuid
#import faiss

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

price_tokenizer = None
price_model = None
sbert_model = None
df = None
text_embeddings = None

BATCH_SIZE = 100

def load_models():
    global price_tokenizer, price_model, sbert_model, df, text_embeddings
    try:
        logger.info("Loading models...")
        model_path = os.getenv('PRICE_MODEL_PATH', 'fine_tuned_price_model')
        price_tokenizer = AutoTokenizer.from_pretrained(model_path)
        price_model = AutoModelForTokenClassification.from_pretrained(model_path)
        logger.info("Price model loaded successfully")

        sbert_model_name = os.getenv('SBERT_MODEL_NAME', 'all-MiniLM-L6-v2')
        sbert_model = SentenceTransformer(sbert_model_name)
        logger.info("SBERT model loaded successfully")

        csv_path = os.getenv('DATASET_PATH', 'swap_dataset.csv')
        df = pd.read_csv(csv_path)
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        df.dropna(subset=['Price'], inplace=True)
        df.reset_index(drop=True, inplace=True)
        logger.info(f"Dataset loaded with {len(df)} items")

        embeddings_path = os.getenv('EMBEDDINGS_PATH', 'sbert_text_embeddings.npy')
        text_embeddings = np.load(embeddings_path)
        logger.info("Text embeddings loaded successfully")
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        raise
    
def setup_payload_indexes():
    try:
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="Category",
            field_schema=PayloadSchemaType.KEYWORD
        )
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="Price",
            field_schema=PayloadSchemaType.FLOAT
        )
        logger.info("Payload indexes created or already exist.")
    except Exception as e:
        logger.warning(f"Could not create payload indexes: {e}")


    
def extract_price_with_finetuned_model(text):
    try:
        inputs = price_tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
        with torch.no_grad():
            outputs = price_model(**inputs)
            predictions = torch.argmax(outputs.logits, dim=2)

        tokens = price_tokenizer.tokenize(text)
        predicted_labels = predictions[0].tolist()[:len(tokens)]
        price_tokens = [token.replace('##', '') for token, label in zip(tokens, predicted_labels) if label in [1, 2]]
        price_str = ''.join(price_tokens)
        price_str = re.sub(r'[^\d.]', '', price_str)

        return float(price_str)
    except Exception as e:
        logger.warning(f"Fine-tuned model failed: {str(e)}, falling back to regex")
        return extract_price_regex_fallback(text)

def extract_price_regex_fallback(text):
    patterns = [
        r'(\d+)\$', r'\$(\d+)', r'(\d+)\s*dollars?', r'(\d+)\s*Dollars?', 
        r'(\d+)\s*USD', r'(\d+)\s*usd', r'(\d+)\s*pounds?', r'(\d+)\s*Pounds?', 
        r'(\d+)\s*[Ee]uro?', r'(\d+)\s*EURO', r'\$\s*(\d+)', r'(\d+)\s*\$',
        r'USD\s*(\d+)', r'usd\s*(\d+)', r'Dollars?\s*(\d+)', r'dollars?\s*(\d+)'
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            try:
                return float(matches[0])
            except:
                continue
    raise ValueError("No price found in text")

def normalize(score, min_s, max_s):
    if max_s == min_s:
        return 0.0
    return (score - min_s) / (max_s - min_s)


def get_recommendations(query_text, category_preference, tolerance=500, limit=10,price_weight=0.7, text_weight=0.3):
    try:
        query_price = extract_price_with_finetuned_model(query_text)
    except:
        return pd.DataFrame(columns=["Description", "Price", "Category", "combined_score"])

    min_price = query_price - tolerance
    max_price = query_price + tolerance

    query_embedding = sbert_model.encode([query_text])[0]
    query_embedding = query_embedding / np.linalg.norm(query_embedding)

    search_results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding.tolist(),
        limit=limit * 5,
        with_payload=True,
        query_filter=Filter(
            must=[
                FieldCondition(key="Category", match=MatchValue(value=category_preference)),
                FieldCondition(key="Price", range=Range(gte=min_price, lte=max_price))
            ]
        )
    )

    if not search_results:
        return pd.DataFrame(columns=["Description", "Price", "Category", "combined_score"])


    scores = [res.score for res in search_results]
    min_score, max_score = min(scores), max(scores)

    result_rows = []
    for res in search_results:
        payload = res.payload
        price = float(payload["Price"])
        price_sim = np.exp(-abs(price - query_price) / 200)
        text_sim_norm = normalize(res.score, min_score, max_score)

        combined_score = price_weight * price_sim + text_weight * text_sim_norm

        result_rows.append({
            "Description": payload["Description"],
            "Price": price,
            "Category": payload["Category"],
            "price_similarity": price_sim,
            "combined_score": combined_score
        })

    result_df = pd.DataFrame(result_rows)
    result_df = result_df.sort_values(by="combined_score", ascending=False).head(limit)
    return result_df


@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "healthy",
        "message": "Advanced Recommendation API",
        "usage": "POST /recommend with {'query': 'item with price', 'category': 'search_category'}",
        "example": {
            "query": "gold necklace 656 usd new",
            "category": "Clothes"
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "recommendation-api"}), 200

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        data = request.get_json()
        if not data or 'query' not in data or 'category' not in data:
            return jsonify({
                "error": "Please provide 'query' and 'category'",
                "example": {
                    "query": "gold necklace 656 usd new",
                    "category": "Clothes"
                }
            }), 400

        query_text = data['query']
        search_category = data['category']
        tolerance = data.get('tolerance', 500)

        logger.info(f"Processing recommendation request: query='{query_text}', category='{search_category}'")
        recommendations = get_recommendations(query_text, search_category, tolerance)

        if recommendations.empty:
            return jsonify({
                "message": f"No recommendations found in category '{search_category}' within specified tolerance",
                "recommendations": [],
                "suggestion": "Try a different category or increase the price tolerance"
            })

        return jsonify({
            "query": query_text,
            "category": search_category,
            "tolerance": tolerance,
            "recommendations": recommendations
        })

    except Exception as e:
        logger.error(f"Error in recommendation endpoint: {str(e)}")
        return jsonify({
            "error": f"Internal server error: {str(e)}"
        }), 500

@app.route('/debug/categories', methods=['GET'])
def debug_categories():
    try:
        categories = df['Category'].value_counts().to_dict()
        return jsonify({
            "available_categories": categories,
            "total_items": len(df)
        })
    except Exception as e:
        logger.error(f"Error in categories debug endpoint: {str(e)}")
        return jsonify({
            "error": f"Error: {str(e)}"
        }), 500

@app.route('/debug/price_range/<category>', methods=['GET'])
def debug_price_range(category):
    try:
        category_items = df[df["Category"].str.contains(category, case=False, na=False)]
        if category_items.empty:
            return jsonify({
                "category": category,
                "message": "No items found in this category"
            })

        return jsonify({
            "category": category,
            "item_count": len(category_items),
            "price_range": {
                "min": float(category_items['Price'].min()),
                "max": float(category_items['Price'].max()),
                "average": float(category_items['Price'].mean())
            },
            "sample_items": category_items[['Description', 'Price']].head(5).to_dict('records')
        })
    except Exception as e:
        logger.error(f"Error in price range debug endpoint: {str(e)}")
        return jsonify({
            "error": f"Error: {str(e)}"
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    load_models()
    setup_payload_indexes() 
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
    
