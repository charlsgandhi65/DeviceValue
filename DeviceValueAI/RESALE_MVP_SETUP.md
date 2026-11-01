# Laptop Resale Value MVP - Setup Instructions

Complete setup guide for the DeviceValue AI Laptop Resale Value MVP.

## Overview

This MVP adds a real-time resale value estimator to your existing DeviceValue AI React frontend. It uses the Freesea Search API to find comparable laptop listings from Indian resale marketplaces and estimates a resale value range.

## Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- npm (comes with Node.js)
- A Freesea API key (free signup at [freesea.dev/dashboard](https://freesea.dev/dashboard))

## Quick Start

### Step 1: Backend Setup

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

5. **Configure environment variables:**

   Copy the example file:
   ```bash
   copy .env.example .env
   ```

   Edit `.env` and add your Freesea API key:
   ```
   FREESEA_API_KEY=your_actual_api_key_here
   ```

   **Get your API key:**
   - Sign up at [freesea.dev/dashboard](https://freesea.dev/dashboard)
   - Click "Create key"
   - Copy the key (shown only once)

6. **Start the backend server:**
   ```bash
   python main.py
   ```

   The backend will run on `http://0.0.0.0:8000`

7. **Verify the backend is running:**
   Open a new terminal and run:
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

### Step 2: Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd Frontend
   ```

2. **Install dependencies (if not already installed):**
   ```bash
   npm install
   ```

3. **Configure environment variables:**

   Copy the example file:
   ```bash
   copy .env.example .env
   ```

   Edit `.env` and set the backend URL:
   ```
   VITE_API_BASE_URL=http://localhost:8000
   ```

4. **Start the frontend development server:**
   ```bash
   npm run dev
   ```

   The frontend will run on `http://localhost:5173`

### Step 3: Use the Application

1. Open your browser and navigate to `http://localhost:5173`

2. You'll see two tabs in the "Laptop valuation tools" section:
   - **ML Price Prediction**: Your existing machine learning price predictor
   - **Resale Value Estimator**: New real-time resale market analysis

3. Click on "Resale Value Estimator" tab

4. Fill in the laptop specifications:
   - Brand and model
   - CPU, RAM, GPU
   - Storage capacity and type
   - Screen size
   - Device age (optional)
   - Physical condition (optional)
   - Battery health (optional)

5. Click "Estimate Resale Value"

6. View the results:
   - Estimated resale range (INR)
   - Comparable listings with source links
   - Limitations and disclaimers

## Running Both Services

You need **two separate terminals** to run both the frontend and backend simultaneously.

### Terminal 1 - Backend:
```bash
cd backend
venv\Scripts\activate
python main.py
```

### Terminal 2 - Frontend:
```bash
cd Frontend
npm run dev
```

## Testing the Integration

### Test Backend Health Endpoint
```bash
curl http://localhost:8000/api/health
```

### Test Resale Estimation Endpoint
```bash
curl -X POST http://localhost:8000/api/resale/estimate \
  -H "Content-Type: application/json" \
  -d "{
    \"brand\": \"Dell\",
    \"model\": \"XPS 15\",
    \"cpu\": \"Intel Core i7-12700H\",
    \"ram\": 16,
    \"gpu\": \"NVIDIA RTX 3050\",
    \"storage_capacity_gb\": 512,
    \"storage_type\": \"SSD\",
    \"screen_size\": 15.6
  }"
```

## File Structure

```
Project/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example         # Environment template
│   ├── .gitignore          # Git ignore rules
│   └── README.md           # Backend documentation
├── Frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ResaleEstimator.jsx    # New resale estimator component
│   │   │   └── ...
│   │   ├── services/
│   │   │   ├── resaleService.js      # New backend API client
│   │   │   └── ...
│   │   ├── pages/
│   │   │   └── Home.jsx              # Updated with tab navigation
│   │   └── ...
│   ├── .env.example         # Updated with backend URL
│   └── ...
└── RESALE_MVP_SETUP.md     # This file
```

## Troubleshooting

### Backend Issues

**Error: FREESEA_API_KEY not configured**
- Ensure you created the `.env` file in the `backend/` directory
- Verify the API key is correctly set: `FREESEA_API_KEY=your_key_here`
- Restart the backend server after adding the API key

**Module not found errors**
- Ensure the virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

**Port 8000 already in use**
- Change the port in `main.py` (line 312): `uvicorn.run(app, host="0.0.0.0", port=8001)`
- Update frontend `.env` to match: `VITE_API_BASE_URL=http://localhost:8001`

### Frontend Issues

**CORS errors when calling backend**
- Ensure backend is running on port 8000
- Check that `VITE_API_BASE_URL` is set correctly in frontend `.env`
- Restart the frontend development server after changing `.env`

**Frontend not loading**
- Ensure you're in the `Frontend/` directory
- Run `npm install` if dependencies are missing
- Check that port 5173 is not already in use

### Integration Issues

**Frontend can't connect to backend**
- Check both terminals are running
- Verify backend health endpoint responds
- Check browser console for error messages
- Ensure no firewall is blocking localhost connections

**No search results returned**
- Verify Freesea API key is valid
- Check that the API key has available quota
- Try different laptop specifications (some may have fewer listings)
- Check backend logs for API errors

## API Key Security

**IMPORTANT:**
- Never commit `.env` files to version control
- Never share your API key publicly
- The `.gitignore` file in `backend/` already excludes `.env`
- Rotate your API key if it's accidentally exposed

## Cost Information

- **Freesea API**: Free tier with generous rate limits (check [freesea.dev/docs/limits](https://freesea.dev/docs/limits))
- No paid services are used in this MVP
- Zero-cost requirement met ✅

## Known Limitations

1. **Estimate accuracy**: Based on asking prices, not confirmed sale prices
2. **Listing freshness**: May include outdated or unavailable listings
3. **Geographic variation**: Prices vary by location within India
4. **Condition factors**: Physical condition and battery health not automatically factored
5. **Data availability**: Some laptop configurations may have insufficient comparable listings
6. **API dependency**: Requires valid Freesea API key to function

## Next Steps (Future Enhancements)

- Integrate physical condition and battery health into estimation algorithm
- Add location-based price adjustments
- Implement listing validation and filtering
- Add historical price tracking
- Create user accounts for saving estimates
- Add price trend charts over time

## Support

For issues with:
- **Backend**: Check `backend/README.md`
- **Frontend**: Check existing DeviceValue AI documentation
- **Freesea API**: Visit [freesea.dev/docs](https://freesea.dev/docs)

## Summary

✅ Backend created with FastAPI
✅ Freesea Search API integrated
✅ Resale estimation endpoint implemented
✅ Frontend connected with new component
✅ Health check endpoint tested
✅ Installation instructions provided
✅ Zero-cost requirement met
✅ Two-hour deadline compatible (minimal implementation)
