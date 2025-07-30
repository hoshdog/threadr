import requests
import json

# API configuration
api_url = "https://threadr-production.up.railway.app/api/generate"
api_key = "zfQBge1AsBBLF8nMNxiHdyFn-_fS7vsTtcTrveXnyD8"
medium_url = "https://medium.com/write-a-catalyst/what-happens-to-old-internet-data-194c22fca281"

# Prepare the request
headers = {
    "Content-Type": "application/json",
    "X-API-Key": api_key
}

payload = {
    "url": medium_url
}

print(f"Testing URL scraping with: {medium_url}")
print(f"API endpoint: {api_url}")
print("-" * 50)

try:
    # Make the POST request
    response = requests.post(api_url, json=payload, headers=headers, timeout=30)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print("-" * 50)
    
    if response.status_code == 200:
        data = response.json()
        print("SUCCESS! Thread generated successfully")
        print(f"Number of tweets: {len(data.get('thread', []))}")
        print("\nGenerated Thread:")
        for i, tweet in enumerate(data.get('thread', []), 1):
            print(f"\nTweet {i}:")
            print(tweet)
            print(f"Length: {len(tweet)} characters")
    else:
        print(f"ERROR: Request failed")
        print(f"Response: {response.text}")
        
except requests.exceptions.Timeout:
    print("ERROR: Request timed out after 30 seconds")
except requests.exceptions.ConnectionError as e:
    print(f"ERROR: Connection failed - {e}")
except Exception as e:
    print(f"ERROR: Unexpected error - {type(e).__name__}: {e}")