# OpenAI Integration Setup for Threadr Backend

## Overview
The Threadr backend uses OpenAI's GPT-3.5-turbo model to intelligently convert articles and text into engaging Twitter/X threads. The integration has been updated to use the latest OpenAI Python library (v1.x).

## Setup Instructions

### 1. Install Dependencies
Make sure you have the latest OpenAI library installed:
```bash
pip install openai>=1.0.0
```

### 2. Configure API Key
You have two options for providing your OpenAI API key:

#### Option A: Environment Variable (Recommended)
Set the `OPENAI_API_KEY` environment variable:
```bash
# Windows
set OPENAI_API_KEY=sk-your-api-key-here

# Linux/Mac
export OPENAI_API_KEY=sk-your-api-key-here
```

#### Option B: API Key File
Create a `.openai_key` file in the backend directory:
```bash
echo "sk-your-api-key-here" > .openai_key
```

**Note:** Make sure to add `.openai_key` to your `.gitignore` file to avoid committing your API key.

## Testing the Integration

Run the test script to verify your OpenAI setup:
```bash
python test_openai.py
```

## How It Works

1. **API Key Loading**: The backend checks for the API key in this order:
   - Environment variable `OPENAI_API_KEY`
   - File `.openai_key` in the backend directory

2. **Client Initialization**: The OpenAI client is initialized at startup using the loaded API key.

3. **Thread Generation**: When generating threads:
   - If the OpenAI client is available, it uses GPT-3.5-turbo to create engaging threads
   - If the client is not available or the API call fails, it falls back to basic text splitting

4. **Error Handling**: The system gracefully handles:
   - Missing API keys (falls back to basic splitting)
   - API errors (logs error and falls back to basic splitting)
   - Rate limiting and other OpenAI errors

## Troubleshooting

### API Key Not Found
If you see "OpenAI API key not found" warning:
1. Check that your API key is correctly set in environment variable or `.openai_key` file
2. Ensure the API key starts with "sk-"
3. Verify file permissions if using `.openai_key` file

### API Errors
If OpenAI API calls fail:
1. Check your API key is valid and has credits
2. Verify you have internet connectivity
3. Check OpenAI service status
4. Review error logs for specific error messages

### Performance Note
The OpenAI API calls are executed asynchronously using a thread pool to avoid blocking the FastAPI async endpoints.