from sentence_transformers import SentenceTransformer, util
import numpy as np

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Example products
products = [
    {"name": "Wireless Bluetooth Headphones", "desc": "Over-ear noise-cancelling headphones with long battery life", "price": 79},
    {"name": "Gaming Laptop", "desc": "High performance laptop with RTX graphics and fast SSD storage", "price": 1299},
    {"name": "Smart Fitness Watch", "desc": "Tracks heart rate, steps, and sleep with waterproof design", "price": 149},
    {"name": "4K Ultra HD TV", "desc": "55-inch smart TV with HDR and streaming apps", "price": 499},
    {"name": "Portable Bluetooth Speaker", "desc": "Compact speaker with deep bass and waterproof design", "price": 59},
    {"name": "Mechanical Keyboard", "desc": "RGB backlit mechanical keyboard for gaming and typing", "price": 99}
]

# Encode product text
product_texts = [f"{p['name']} - {p['desc']}" for p in products]
product_embeddings = model.encode(product_texts, convert_to_tensor=True)

# Normalize prices (0-1 range)
prices = np.array([p["price"] for p in products], dtype=float)
max_price = prices.max()
normalized_prices = prices / max_price

# User query and target price
user_query = "Waterproof speaker for outdoor use"
target_price = 70  # user budget or preferred price

# Encode query
user_embedding = model.encode(user_query, convert_to_tensor=True)

# Calculate text similarity
text_similarities = util.cos_sim(user_embedding, product_embeddings)[0].cpu().numpy()

# Calculate price similarity (closer prices get higher score)
normalized_target_price = target_price / max_price
price_similarities = 1 - np.abs(normalized_prices - normalized_target_price)

# Combine similarities with weights
alpha = 0.7  # weight for text
beta = 0.3   # weight for price
final_scores = alpha * text_similarities + beta * price_similarities

# Get top results
top_indices = np.argsort(-final_scores)[:3]
print("Top recommendations for:", user_query, "with budget $", target_price)
for idx in top_indices:
    p = products[idx]
    print(f"- {p['name']} (${p['price']}): {p['desc']} | Score: {final_scores[idx]:.4f}")
