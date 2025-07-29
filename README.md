# Threadr - Twitter Thread Generator

A simple SaaS tool that converts blog articles or pasted content into engaging Twitter threads.

## Quick Start

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Make sure your OpenAI API key is in `backend/.openai_key`

4. Start the backend server:
   ```bash
   python -m uvicorn main:app --reload --port 8000
   ```

   The API will be available at http://localhost:8000

### Frontend Setup

1. Open `frontend/index.html` in your web browser
   - Or use a local server: `python -m http.server 8080` in the frontend directory
   - Then visit http://localhost:8080

## Features

- URL or text input
- AI-powered thread generation
- Inline tweet editing
- Character counting
- Copy individual tweets or entire thread
- Email capture for future features

## API Endpoints

- `GET /` - API information
- `POST /api/generate` - Generate thread from URL or text
- `GET /health` - Health check
- `GET /api/rate-limit-status` - Check rate limit status

## Rate Limiting

- 10 requests per hour per IP address
- Resets automatically after one hour