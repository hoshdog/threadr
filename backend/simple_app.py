"""
Ultra-simple FastAPI test for Railway deployment debugging
"""
from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello from Railway!", "status": "ok"}

@app.get("/health")
def health():
    return {"status": "healthy", "port": os.environ.get("PORT", "unknown")}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)