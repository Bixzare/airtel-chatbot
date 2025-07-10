# Backend Deployment Guide

## Local Development

### Running the server locally:
```bash
# Method 1: Run the main.py file directly
python src/api/main.py

# Method 2: Use the run_api.py script
python run_api.py

# Method 3: Use uvicorn directly
python -m uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000
```

### Testing locally:
```bash
# Run the test script
python test_local.py
```

## Vercel Deployment

### Files configured for Vercel:

1. **`app.py`** - Entry point that imports the FastAPI app
2. **`vercel.json`** - Vercel configuration
3. **`src/api/main.py`** - Main FastAPI application with health check endpoint

### Deployment Steps:

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm install -g vercel
   ```

2. **Deploy to Vercel**:
   ```bash
   # From the backend directory
   vercel
   
   # Or for production
   vercel --prod
   ```

3. **Environment Variables** (if needed):
   - Set any required environment variables in your Vercel dashboard
   - The app will automatically use the `PORT` environment variable provided by Vercel

### API Endpoints:

- **GET `/`** - Health check endpoint
- **POST `/chat`** - Chat endpoint for RAG agent
  ```json
  {
    "session_id": "unique_session_id",
    "message": "Your message here"
  }
  ```

### Troubleshooting:

1. **Import Errors**: Make sure all dependencies are in `requirements.txt`
2. **Port Issues**: The app automatically uses the `PORT` environment variable
3. **Health Check**: The `/` endpoint returns a 200 status for Vercel's health checks

### Local vs Production:

- **Local**: Uses `127.0.0.1:8000` with reload enabled
- **Production**: Uses `0.0.0.0:$PORT` with reload disabled
- **Vercel**: Automatically detects and uses the FastAPI app instance 