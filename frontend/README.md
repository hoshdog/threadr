# Threadr Frontend

A modern, responsive frontend for converting articles to Twitter threads, built with Alpine.js and Tailwind CSS.

## Features

- ✅ URL and text input modes
- ✅ Real-time tweet editing
- ✅ Character count validation
- ✅ Copy individual tweets or entire thread
- ✅ Responsive design
- ✅ Email capture modal
- ✅ Production-ready error handling
- ✅ Environment-aware configuration

## Quick Start

### Local Development

1. **Start local server:**
   ```bash
   # Using Python
   python -m http.server 3000
   
   # Using Node.js serve
   npx serve . -p 3000
   
   # Using any static server
   ```

2. **Open in browser:**
   ```
   http://localhost:3000
   ```

3. **Test connection:**
   ```
   http://localhost:3000/test-connection.html
   ```

### Production Deployment (Vercel)

1. **Install Vercel CLI:**
   ```bash
   npm i -g vercel
   ```

2. **Set Environment Variables:**
   ```bash
   # Set production API URL
   vercel env add THREADR_API_URL production https://threadr-production.up.railway.app
   
   # Set for preview environments
   vercel env add THREADR_API_URL preview https://threadr-production.up.railway.app
   ```

3. **Deploy:**
   ```bash
   # Preview deployment
   vercel
   
   # Production deployment
   vercel --prod
   ```

## Configuration

The app automatically detects the environment and configures itself:

- **Development** (`localhost`): Uses `http://localhost:8000` backend
- **Preview** (`*.vercel.app`): Uses Railway production backend
- **Production** (custom domain): Uses Railway production backend

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `THREADR_API_URL` | Backend API URL | `https://threadr-production.up.railway.app` |
| `THREADR_DEBUG` | Enable debug mode | Auto-detected |
| `THREADR_ENV` | Force environment | Auto-detected |

## File Structure

```
frontend/
├── index.html              # Main application
├── config.js              # Configuration and environment detection
├── vercel.json            # Vercel deployment configuration
├── test-connection.html   # Backend connection testing tool
├── deploy.md             # Detailed deployment guide
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Architecture

### Frontend Stack
- **Alpine.js**: Reactive JavaScript framework
- **Tailwind CSS**: Utility-first CSS framework
- **Vanilla HTML/JS**: No build process required

### Backend Integration
- **RESTful API**: Communicates with FastAPI backend
- **CORS Enabled**: Proper cross-origin request handling
- **Error Resilience**: Graceful fallback and error messages
- **Request Timeout**: 30-second timeout with abort controller

### Security Features
- **CSP Headers**: Content Security Policy
- **HSTS**: HTTP Strict Transport Security
- **Frame Protection**: X-Frame-Options
- **XSS Protection**: Built-in XSS prevention

## API Endpoints Used

### POST `/api/generate`
Generate Twitter thread from URL or text.

**Request:**
```json
{
  "url": "https://example.com/article"
}
// OR
{
  "text": "Article content here..."
}
```

**Response:**
```json
{
  "thread": [
    {
      "content": "Tweet 1 content...",
      "order": 1
    }
  ]
}
```

### POST `/api/subscribe` (Optional)
Subscribe email for updates.

**Request:**
```json
{
  "email": "user@example.com"
}
```

## Testing

### Connection Test
Open `test-connection.html` to verify:
- Backend connectivity
- CORS configuration
- API endpoint functionality
- Response times

### Manual Testing
1. **URL Mode**: Test with a real article URL
2. **Text Mode**: Test with pasted content
3. **Error Handling**: Test with invalid URLs
4. **Character Limits**: Test tweet length validation
5. **Copy Functionality**: Test copy buttons

## Troubleshooting

### Backend Connection Issues
1. Check `test-connection.html` for diagnostics
2. Verify Railway backend is running
3. Check browser console for CORS errors
4. Enable fallback mode:
   ```js
   localStorage.setItem('threadr_allow_fallback', 'true')
   ```

### Deployment Issues
1. Check Vercel environment variables
2. Verify `vercel.json` configuration
3. Check build logs in Vercel dashboard
4. Test with `vercel dev` locally

### CORS Issues
- Backend must include frontend domain in CORS origins
- Check Network tab for preflight requests
- Verify `Access-Control-Allow-Origin` headers

## Browser Support

- ✅ Chrome 80+
- ✅ Firefox 75+
- ✅ Safari 13.1+
- ✅ Edge 80+

## Performance

- **First Load**: < 2 seconds
- **Subsequent Loads**: < 500ms (cached)
- **API Response**: < 10 seconds typical
- **Bundle Size**: ~50KB (including CDN resources)

## Contributing

1. Make changes to source files
2. Test locally with `python -m http.server 3000`
3. Use `test-connection.html` to verify backend integration
4. Deploy to Vercel preview for testing
5. Deploy to production when ready

## License

This project is part of the Threadr application.