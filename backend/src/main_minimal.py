"""
Ultra-minimal FastAPI app for Railway debugging
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime

# Create app
app = FastAPI(title="Threadr Minimal", version="1.0.0")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "app": "Threadr Minimal",
        "version": "1.0.0",
        "deployment": "main_minimal.py",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "app": "minimal",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/generate")
async def generate(request: Request):
    body = await request.json()
    content = body.get("content", "No content provided")
    
    # Simple tweet splitting
    words = content.split()
    tweets = []
    current = []
    length = 0
    
    for word in words:
        if length + len(word) + 1 > 280:
            tweets.append(" ".join(current))
            current = [word]
            length = len(word)
        else:
            current.append(word)
            length += len(word) + 1
    
    if current:
        tweets.append(" ".join(current))
    
    return {
        "success": True,
        "tweets": tweets[:5],  # Max 5 tweets
        "count": len(tweets[:5])
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)