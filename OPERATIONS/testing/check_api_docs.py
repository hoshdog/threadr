#!/usr/bin/env python3
"""
Check API Documentation for Available Endpoints
===============================================
"""

import requests
import json

BACKEND_URL = "https://threadr-pw0s.onrender.com"

def get_openapi_spec():
    """Get OpenAPI specification"""
    try:
        response = requests.get(f"{BACKEND_URL}/openapi.json", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get OpenAPI spec: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting OpenAPI spec: {e}")
        return None

def analyze_endpoints(openapi_spec):
    """Analyze available endpoints from OpenAPI spec"""
    if not openapi_spec or "paths" not in openapi_spec:
        print("No paths found in OpenAPI spec")
        return
    
    print("AVAILABLE ENDPOINTS FROM API DOCUMENTATION:")
    print("=" * 60)
    
    paths = openapi_spec["paths"]
    
    # Group by category
    auth_endpoints = []
    thread_endpoints = []
    generate_endpoints = []
    other_endpoints = []
    
    for path, methods in paths.items():
        for method, details in methods.items():
            endpoint_info = {
                "path": path,
                "method": method.upper(),
                "summary": details.get("summary", ""),
                "tags": details.get("tags", [])
            }
            
            if "auth" in path.lower() or "login" in path.lower() or "register" in path.lower():
                auth_endpoints.append(endpoint_info)
            elif "thread" in path.lower():
                thread_endpoints.append(endpoint_info)
            elif "generate" in path.lower():
                generate_endpoints.append(endpoint_info)
            else:
                other_endpoints.append(endpoint_info)
    
    # Print categorized endpoints
    categories = [
        ("AUTHENTICATION ENDPOINTS", auth_endpoints),
        ("THREAD MANAGEMENT ENDPOINTS", thread_endpoints),
        ("GENERATION ENDPOINTS", generate_endpoints),
        ("OTHER ENDPOINTS", other_endpoints)
    ]
    
    for category_name, endpoints in categories:
        if endpoints:
            print(f"\n{category_name}:")
            print("-" * 40)
            for ep in endpoints:
                tags = ", ".join(ep["tags"]) if ep["tags"] else "No tags"
                print(f"{ep['method']:<7} {ep['path']:<30} {ep['summary']}")
                print(f"        Tags: {tags}")
        else:
            print(f"\n{category_name}:")
            print("-" * 40)
            print("No endpoints found in this category")

def main():
    """Main function"""
    print(f"Analyzing API documentation from: {BACKEND_URL}/docs")
    print("=" * 60)
    
    # Get OpenAPI spec
    spec = get_openapi_spec()
    
    if spec:
        print(f"API Info:")
        print(f"  Title: {spec.get('info', {}).get('title', 'Unknown')}")
        print(f"  Version: {spec.get('info', {}).get('version', 'Unknown')}")
        print(f"  Description: {spec.get('info', {}).get('description', 'None')}")
        print()
        
        # Analyze endpoints
        analyze_endpoints(spec)
        
        # Check if auth is mentioned in components/schemas
        if "components" in spec and "schemas" in spec["components"]:
            schemas = spec["components"]["schemas"]
            auth_schemas = [name for name in schemas.keys() if "auth" in name.lower() or "user" in name.lower()]
            if auth_schemas:
                print(f"\nAUTH-RELATED SCHEMAS FOUND:")
                print("-" * 40)
                for schema in auth_schemas:
                    print(f"  - {schema}")
            else:
                print(f"\nNO AUTH-RELATED SCHEMAS FOUND")
        
    else:
        print("Could not retrieve API documentation")
        
    print(f"\nTo view the interactive docs, visit: {BACKEND_URL}/docs")

if __name__ == "__main__":
    main()