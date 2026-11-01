# DeviceValue AI Backend

FastAPI backend for the DeviceValue AI Laptop Resale Value MVP.

## Features

- **FastAPI** backend with CORS configured for local frontend
- **Freesea Search API** integration for finding used laptop listings
- **Resale value estimation** based on comparable market listings
- **Health check endpoint** for monitoring backend status

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

## Installation

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**

   **Windows (Git Bash / Command Prompt):**
   ```bash
   venv\Scripts\activate
   ```

   **Windows (PowerShell):**
   ```powershell
   venv\Scripts\Activate.ps1
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. **Get a Freesea API key:**
   - Sign up at [freesea.dev/dashboard](https://freesea.dev/dashboard)
   - Create a new API key
   - Copy the key (it's shown only once)

2. **Create environment file:**
   ```bash
   # Copy the example file
   copy .env.example .env
   ```

3. **Edit `.env` file and add your API key:**
   ```
   FREESEA_API_KEY=your_actual_api_key_here
   ```

   **Important:** Never commit the `.env` file or your API key to version control.

## Running the Backend

1. **Make sure the virtual environment is activated**

2. **Start both servers:**
   ```bash
   python main.py
   ```

   This starts:
   - Frontend: `http://127.0.0.1:5173`
   - Backend: `http://127.0.0.1:8000`

   Open `http://127.0.0.1:5173` in your browser. Press `Ctrl+C` in the terminal
   to stop both servers.

3. **Verify health check:**
   ```bash
   curl http://localhost:8000/api/health
   ```

   Expected response:
   ```json
   {
     "status": "healthy",
     "timestamp": "2026-10-17T11:51:05.036528",
     "freesea_configured": true
   }
   ```

## API Endpoints

### GET /api/health
Health check endpoint to verify backend status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-10-17T11:51:05.036528",
  "freesea_configured": true
}
```

### POST /api/resale/estimate
Estimate resale value for a laptop based on market listings.

**Request Body:**
```json
{
  "brand": "Dell",
  "model": "XPS 15",
  "cpu": "Intel Core i7-12700H",
  "ram": 16,
  "gpu": "NVIDIA RTX 3050",
  "storage_capacity_gb": 512,
  "storage_type": "SSD",
  "screen_size": 15.6,
  "device_age_years": 2.5,
  "physical_condition": "good",
  "battery_health": "85%"
}
```

**Response (Success):**
```json
{
  "status": "success",
  "estimated_range_min": 45000,
  "estimated_range_max": 65000,
  "estimated_range_min_inr": 45000,
  "estimated_range_max_inr": 65000,
  "currency": "INR",
  "comparable_listings_count": 5,
  "listings": [...],
  "retrieval_timestamp": "2026-10-17T11:51:05.036528",
  "limitations": [...]
}
```

**Response (Insufficient Data):**
```json
{
  "status": "insufficient_data",
  "comparable_listings_count": 2,
  "listings": [...],
  "retrieval_timestamp": "2026-10-17T11:51:05.036528",
  "limitations": [
    "Estimates based on asking prices, not confirmed sale prices",
    "Results from web search may include outdated or unavailable listings",
    "Insufficient comparable listings with prices (found 2, need at least 3)"
  ]
}
```

## Project Structure

```
backend/
├── main.py              # FastAPI application with endpoints
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Limitations

- Estimates are based on **asking prices**, not confirmed sale prices
- Results from web search may include outdated or unavailable listings
- Market prices vary by location, seller, and exact condition
- Physical condition and battery health are not factored into automated estimate
- Requires valid Freesea API key to function

## Troubleshooting

**Error: FREESEA_API_KEY not configured**
- Ensure you created the `.env` file
- Verify the API key is correctly set in the `.env` file
- Restart the server after adding the API key

**Module not found errors**
- Ensure the virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

**CORS errors in frontend**
- Ensure backend is running on port 8000
- Check that frontend's `VITE_API_BASE_URL` is set to `http://localhost:8000`
