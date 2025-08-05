import requests
import json
import time

# API configuration
api_url = "https://threadr-production.up.railway.app/api/generate"
api_key = "your-api-key-here"
medium_url = "https://medium.com/write-a-catalyst/what-happens-to-old-internet-data-194c22fca281"

# Test cases
test_cases = [
    {
        "name": "Medium Article URL",
        "payload": {"url": medium_url}
    },
    {
        "name": "Simple Text Content",
        "payload": {
            "text": "This is a test article about what happens to old internet data. " * 10
        }
    }
]

headers = {
    "Content-Type": "application/json",
    "X-API-Key": api_key
}

print("=" * 70)
print("THREADR API COMPREHENSIVE TEST")
print("=" * 70)

for test_case in test_cases:
    print(f"\nTest: {test_case['name']}")
    print("-" * 50)
    
    start_time = time.time()
    
    try:
        # Make the POST request
        response = requests.post(
            api_url, 
            json=test_case['payload'], 
            headers=headers, 
            timeout=60
        )
        
        elapsed_time = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {elapsed_time:.2f} seconds")
        print(f"Response Headers: {dict(response.headers)}")
        print("-" * 50)
        
        if response.status_code == 200:
            data = response.json()
            print("SUCCESS!")
            print(f"Source Type: {data.get('source_type', 'unknown')}")
            print(f"Title: {data.get('title', 'No title')}")
            print(f"Number of tweets: {len(data.get('thread', []))}")
            
            if 'thread' in data and data['thread']:
                print("\nFirst 3 tweets:")
                for i, tweet in enumerate(data['thread'][:3], 1):
                    print(f"\nTweet {i}/{len(data['thread'])}:")
                    print(f"Content: {tweet['content']}")
                    print(f"Characters: {tweet['character_count']}")
        else:
            print("ERROR!")
            try:
                error_data = response.json()
                print(f"Error Detail: {error_data.get('detail', 'No detail provided')}")
                if 'error_id' in error_data:
                    print(f"Error ID: {error_data['error_id']}")
            except:
                print(f"Raw Response: {response.text[:500]}")
                
    except requests.exceptions.Timeout:
        print("ERROR: TIMEOUT ERROR - Request took longer than 60 seconds")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ CONNECTION ERROR: {e}")
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {type(e).__name__}: {e}")
    
    print("\n" + "=" * 70)

# Test direct URL fetch capability
print("\nTesting Direct URL Fetch (bypassing API)...")
print("-" * 50)

try:
    direct_response = requests.get(
        medium_url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
        timeout=10
    )
    print(f"Direct fetch status: {direct_response.status_code}")
    print(f"Content length: {len(direct_response.content)} bytes")
    print(f"Content type: {direct_response.headers.get('content-type', 'unknown')}")
except Exception as e:
    print(f"Direct fetch failed: {type(e).__name__}: {e}")