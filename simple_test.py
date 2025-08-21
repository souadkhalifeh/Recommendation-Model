import requests
import json

# Test if API is running
try:
    response = requests.get("http://localhost:8000/products/")
    print(f"API Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test adding a product
    product_data = {
        "name": "Test Product",
        "desc": "A test product for verification",
        "price": 50.0
    }
    
    add_response = requests.post("http://localhost:8000/products/", json=product_data)
    print(f"\nAdd Product Status: {add_response.status_code}")
    print(f"Add Response: {add_response.json()}")
    
except Exception as e:
    print(f"Error: {e}")
