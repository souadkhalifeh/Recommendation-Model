import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_add_product():
    """Test adding a product to the database"""
    url = f"{BASE_URL}/products/"
    
    # Sample product data
    product = {
        "name": "Wireless Bluetooth Headphones",
        "desc": "Over-ear noise-cancelling headphones with long battery life",
        "price": 79
    }
    
    # Send POST request
    response = requests.post(url, json=product)
    print(f"Add Product Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    return response.json().get("id")

def test_add_multiple_products():
    """Test adding multiple products to the database"""
    url = f"{BASE_URL}/products/"
    
    # Sample products from the original recommendation sample
    products = [
        {"name": "Gaming Laptop", "desc": "High performance laptop with RTX graphics and fast SSD storage", "price": 1299},
        {"name": "Smart Fitness Watch", "desc": "Tracks heart rate, steps, and sleep with waterproof design", "price": 149},
        {"name": "4K Ultra HD TV", "desc": "55-inch smart TV with HDR and streaming apps", "price": 499},
        {"name": "Portable Bluetooth Speaker", "desc": "Compact speaker with deep bass and waterproof design", "price": 59},
        {"name": "Mechanical Keyboard", "desc": "RGB backlit mechanical keyboard for gaming and typing", "price": 99}
    ]
    
    product_ids = []
    for product in products:
        response = requests.post(url, json=product)
        if response.status_code == 201:
            product_ids.append(response.json().get("id"))
            print(f"Added product: {product['name']}")
    
    return product_ids

def test_list_products():
    """Test listing all products in the database"""
    url = f"{BASE_URL}/products/"
    
    # Send GET request
    response = requests.get(url)
    print(f"List Products Status Code: {response.status_code}")
    
    # Print products
    products = response.json().get("products", [])
    print(f"Total products: {len(products)}")
    for product in products:
        print(f"- {product['name']} (${product['price']}): {product['description']}")
    
    return products

def test_get_recommendations():
    """Test getting recommendations based on a query"""
    url = f"{BASE_URL}/recommendations/"
    
    # Sample recommendation request
    request_data = {
        "query": "Waterproof speaker for outdoor use",
        "target_price": 70,
        "num_results": 3,
        "alpha": 0.7,
        "beta": 0.3
    }
    
    # Send POST request
    response = requests.post(url, json=request_data)
    print(f"Get Recommendations Status Code: {response.status_code}")
    
    # Print recommendations
    recommendations = response.json().get("recommendations", [])
    print(f"Query: {request_data['query']} with budget ${request_data['target_price']}")
    print(f"Total recommendations: {len(recommendations)}")
    for rec in recommendations:
        print(f"- {rec['name']} (${rec['price']}): {rec['description']} | Score: {rec['score']:.4f}")
    
    return recommendations

if __name__ == "__main__":
    print("=== Testing API ===")
    
    # Add a single product
    product_id = test_add_product()
    print(f"\nAdded product with ID: {product_id}")
    
    # Add multiple products
    print("\n=== Adding multiple products ===")
    product_ids = test_add_multiple_products()
    print(f"Added {len(product_ids)} products")
    
    # List all products
    print("\n=== Listing all products ===")
    products = test_list_products()
    
    # Get recommendations
    print("\n=== Getting recommendations ===")
    recommendations = test_get_recommendations()
