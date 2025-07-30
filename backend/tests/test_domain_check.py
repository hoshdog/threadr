import requests
import json

# API configuration
api_url = "https://threadr-production.up.railway.app/api/generate"
api_key = "zfQBge1AsBBLF8nMNxiHdyFn-_fS7vsTtcTrveXnyD8"

# Test with a domain that's likely not whitelisted
test_urls = [
    "https://example.com/test-article",
    "https://medium.com/write-a-catalyst/what-happens-to-old-internet-data-194c22fca281",
    "https://dev.to/test-article",
    "https://blog.medium.com/test"
]

headers = {
    "Content-Type": "application/json",
    "X-API-Key": api_key
}

print("Testing Domain Whitelist Configuration")
print("=" * 50)

for test_url in test_urls:
    print(f"\nTesting: {test_url}")
    
    try:
        response = requests.post(
            api_url,
            json={"url": test_url},
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            try:
                error_data = response.json()
                detail = error_data.get('detail', 'No detail')
                print(f"Error: {detail}")
                
                # Look for domain-related errors
                if "domain" in detail.lower() or "allowed" in detail.lower():
                    print("-> This appears to be a domain whitelist issue")
                elif "internal server error" in detail.lower():
                    print(f"-> Internal error (ID: {detail.split('Error ID: ')[-1] if 'Error ID:' in detail else 'unknown'})")
                    
            except:
                print(f"Raw response: {response.text[:200]}")
    
    except Exception as e:
        print(f"Request failed: {type(e).__name__}: {e}")