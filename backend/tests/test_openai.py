#!/usr/bin/env python3
"""Test script to verify OpenAI integration"""

import os
import sys
from openai import OpenAI, OpenAIError

def test_openai_integration():
    """Test the OpenAI client setup and API call"""
    
    # Load API key
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        key_file_path = os.path.join(os.path.dirname(__file__), ".openai_key")
        if os.path.exists(key_file_path):
            with open(key_file_path, "r") as f:
                api_key = f.read().strip()
    
    if not api_key:
        print("ERROR: OpenAI API key not found!")
        print("Please set OPENAI_API_KEY environment variable or create a .openai_key file")
        return False
    
    print(f"API key found: {api_key[:8]}...{api_key[-4:]}")
    
    try:
        # Initialize client
        client = OpenAI(api_key=api_key)
        print("✓ OpenAI client initialized successfully")
        
        # Test API call
        print("\nTesting API call...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello, World!' in exactly 3 words."}
            ],
            temperature=0.7,
            max_tokens=10
        )
        
        print(f"✓ API call successful!")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except OpenAIError as e:
        print(f"✗ OpenAI API error: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing OpenAI integration for Threadr backend...")
    print("-" * 50)
    success = test_openai_integration()
    print("-" * 50)
    sys.exit(0 if success else 1)