import requests
import json

# Test the API endpoints
base_url = "http://localhost:8000"

# Test root endpoint
print("Testing root endpoint...")
response = requests.get(f"{base_url}/")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

# Test health endpoint
print("Testing health endpoint...")
response = requests.get(f"{base_url}/health")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

# Test thread generation with text
print("Testing thread generation with text...")
test_content = """
Artificial Intelligence is transforming the way we live and work. From healthcare to transportation, 
AI systems are making processes more efficient and opening new possibilities. Machine learning algorithms 
can now diagnose diseases, drive cars, and even create art. However, with great power comes great responsibility. 
We must ensure AI is developed ethically and benefits humanity as a whole.
"""

response = requests.post(
    f"{base_url}/api/generate",
    json={"content": test_content}
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Generated {len(data['tweets'])} tweets:")
    for i, tweet in enumerate(data['tweets'], 1):
        print(f"\nTweet {i}:")
        print(tweet['text'])
        print(f"Characters: {tweet['char_count']}")
else:
    print(f"Error: {response.json()}")

# Test rate limit status
print("\n\nTesting rate limit status...")
response = requests.get(f"{base_url}/api/rate-limit-status")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")