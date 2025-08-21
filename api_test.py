import requests
import json

API_URL = "https://recommendation-model-469048844145.europe-west1.run.app"

def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{API_URL}/health")
        print("Health Check Status:", response.status_code)
        print("Response:", response.json())
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {str(e)}")
        return False

def test_recommendation_check():
    """Test the /recommend endpoint with better debugging"""
    test_data = {
        "query": "gold necklace 656 usd new",
        "category": "Clothes"
    }
    try:
        response = requests.post(
            f"{API_URL}/recommend",
            headers={"Content-Type": "application/json"},
            data=json.dumps(test_data),
        )
        print("\n[Recommendation]", response.status_code)
        if response.status_code == 200:
            print("Response:", json.dumps(response.json(), indent=2))
        else:
            print("Error:", response.text)
            
        return response.status_code == 200
    except Exception as e:
        print(f"Recommendation request failed: {str(e)}")
        return False
    
    
if __name__ == "__main__":
    print("=== Testing Recommendation System API ===")
    
    print("\n1. Testing health check...")
    health_ok = test_health_check()
    
    if health_ok:
        print("\n2. Testing item recommendation...")
        plan_ok = test_recommendation_check()
    else:
        print("\nSkipping item recommendation test due to health check failure")
        plan_ok = False
    
    print("\n=== Test Summary ===")
    print(f"Health Check: {'PASSED' if health_ok else 'FAILED'}")
    if health_ok:
        print(f"Item Recommendation: {'PASSED' if plan_ok else 'FAILED'}")
