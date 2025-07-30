import requests
import json

# API configuration
base_url = "https://threadr-production.up.railway.app"

endpoints = [
    "/health",
    "/readiness",
    "/debug/startup"
]

print("Testing health endpoints...")
print("-" * 50)

for endpoint in endpoints:
    url = base_url + endpoint
    print(f"\nTesting: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
            except:
                print(f"Response: {response.text}")
        else:
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")