# 📱 Phone Resale Pro

> AI-powered smartphone resale valuation platform that estimates the fair market price of used phones in INR using Machine Learning, real device configurations, battery health, condition, and depreciation trends.

Built with **Python • pandas • scikit-learn • Streamlit • Plotly**

---

## 🌐 Live Demo

https://phone-resale-pro-hqpuqumrow8ujppd5rjcuz.streamlit.app/

---

## ✨ Overview

Phone Resale Pro helps users instantly estimate the resale value of used smartphones in the Indian market.

Instead of manually guessing prices, the platform uses a trained ML model and multiple real-world factors such as age, battery health, RAM, storage, condition, and original launch price to generate a smart valuation.

This project was upgraded using a cleaned dataset, realistic phone variants, and retrained ML models for stronger accuracy and better market realism.

---

## 🚀 Key Highlights

- 📊 AI-powered resale price prediction
- 📱 5000+ training records
- 🧠 Retrained ML model with cleaner dataset
- 🔋 Battery health aware pricing
- 📆 Age-based depreciation logic
- 💾 Real RAM / Storage variant filtering
- 📈 Lifecycle value forecast chart
- 🎯 Premium futuristic UI
- ⚡ Instant predictions
- 📲 Mobile responsive design

---

## 💡 What Makes This Project Better

Unlike basic estimators, Phone Resale Pro includes:

### ✅ Cleaned Dataset

Removed unrealistic training rows such as impossible RAM / storage combinations.

### ✅ Real Device Configurations

Dropdown selections only show valid real-world variants for supported models.

### ✅ Better Prediction Logic

Retrained model gives more realistic prices across:

- Apple flagships
- Samsung Ultra devices
- Midrange Android phones
- Budget phones

### ✅ Premium User Experience

Glassmorphism dashboard with smooth visuals and responsive layout.

---

## 🧠 How It Works

```text
User Input
   ↓
Device Config Validation
   ↓
Feature Processing
   ↓
Machine Learning Prediction
   ↓
Market Estimate + Insights Dashboard
```

---

## 📊 Prediction Factors Used

| Factor | Description |
|-------|-------------|
| Brand | Apple, Samsung, Xiaomi, etc. |
| Model | Specific smartphone model |
| RAM | Device RAM in GB |
| Storage | Internal storage in GB |
| Age | Phone age in months |
| Battery Health | Estimated battery condition |
| Visual Condition | Excellent / Good / Fair / Poor |
| Launch Price | Original retail launch price |

---

## 📱 Supported Brands

- Apple  
- Samsung  
- Xiaomi  
- OnePlus  
- Google  
- Vivo  
- Oppo  
- Realme  
- Motorola  
- Nothing  
- IQOO  
- Nokia  

---

## 🚀 Live Features

- Fair resale value estimate
- Suggested price range
- Retention percentage vs launch price
- Future depreciation forecast
- Real device image fetching
- Variant-aware RAM & storage selection
- Mobile-friendly experience
- Fast response UI

---

## 🛠 Tech Stack

| Category | Tools |
|---------|------|
| Language | Python |
| Data Handling | pandas, NumPy |
| ML Model | scikit-learn Random Forest Regressor |
| Frontend | Streamlit |
| Charts | Plotly |
| Deployment | Streamlit Cloud |
| Version Control | Git + GitHub |

---

## 📂 Project Structure

```text
phone-resale-pro/
│
├── data/
│   ├── used_phones_clean.csv
│   └── phone_variants.csv
│
├── model/
│   ├── model.pkl
│   └── encoders.pkl
│
├── streamlit_app.py
├── predict.py
├── train_model.py
├── generate_2000_rows.py
├── requirements.txt
└── README.md
```

---

## ⚙️ Machine Learning Pipeline

```text
Raw Dataset
   ↓
Data Cleaning
   ↓
Variant Validation
   ↓
Encoding Categorical Features
   ↓
Train/Test Split
   ↓
Random Forest Regressor
   ↓
Evaluation
   ↓
Deployment
```

---

## 📈 Model Improvements

Recent upgrades included:

- Cleaned fake / impossible data rows
- Added 5000+ realistic records
- Expanded supported device variants
- Better flagship pricing behavior
- Better midrange and budget predictions
- Improved consistency across brands

---

## ⚡ Installation & Run Locally

### 1️⃣ Clone Repository

```bash
git clone https://github.com/sayakbhattasali/phone-resale-pro.git
cd phone-resale-pro
```

### 2️⃣ Install Requirements

```bash
pip install -r requirements.txt
```

### 3️⃣ Launch App

```bash
streamlit run streamlit_app.py
```

---

## 🔁 Retrain Model

If dataset changes:

```bash
python train_model.py
```

---
---

## 🔮 Future Improvements

- Live OLX / Cashify market integration
- Confidence score prediction
- User login system
- Saved prediction history
- Compare two devices
- Explainable AI price breakdown
- API version for external apps
- Mobile app version

---

## ⚠ Disclaimer

Predicted prices are estimated values based on training data and machine learning outputs. Actual resale value may vary depending on city, market demand, seller urgency, and device condition.

---

## 👨‍💻 Author

**Sayak Bhattasali**

- GitHub: https://github.com/sayakbhattasali

---

## ⭐ Support

If you liked this project, consider giving the repository a star.

--- 
## 🏆 Project Value

This project demonstrates skills in:

- Machine Learning
- Data Cleaning
- Feature Engineering
- Python Development
- UI Design
- Deployment
- GitHub Workflow
- Real-world Product Thinking
