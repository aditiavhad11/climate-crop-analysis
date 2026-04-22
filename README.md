# climate-crop-analysis
# 🌾 CropAI — Smart Crop Prediction & Analytics System

## 🚀 Overview

CropAI is a Machine Learning–based web application that helps users:

* Predict crop production
* Get smart crop recommendations
* Analyze agricultural data using dashboards
* Compare ML models
* Forecast future crop production

The system combines **Flask (backend)**, **Machine Learning (Random Forest & Linear Regression)**, and **interactive frontend (HTML, CSS, JS, Chart.js)**.



## 🎯 Features

### 🔮 1. Crop Production Prediction

* Predicts production based on:

  * Crop
  * Season
  * Rainfall
  * Area
* Uses **Random Forest Regressor**

---

### 🌱 2. Smart Crop Recommendation

* Suggests best crops based on:

  * State & District
  * Rainfall
  * Area
* Hybrid approach:

  * ML prediction
  * Real dataset filtering

---

### 📊 3. Analytics Dashboard

* Donut Chart → Crop distribution
* Bar Chart → Production comparison
* State-based filtering
* Built using **Chart.js**

---

### ⚖️ 4. Model Comparison

* Compare:

  * Random Forest
  * Linear Regression
* Metrics:

  * R² Score
  * MSE (Mean Squared Error)
* Highlights best model

---

### 📈 5. Forecasting

* Predicts future production (2–5 years)
* Based on **trend analysis (time-series)**
* Shows:

  * Historical data
  * Predicted values
  * Confidence interval (upper/lower bounds)

---

## 🧠 Machine Learning

### Models Used:

* 🌳 Random Forest Regressor (Main model)
* 📉 Linear Regression (Comparison)

### Evaluation Metrics:

* R² Score
* MSE (Mean Squared Error)
* RMSE



## 🛠️ Tech Stack

### Backend:

* Python
* Flask

### Frontend:

* HTML
* CSS
* JavaScript

### Visualization:

* Chart.js

### ML Libraries:

* scikit-learn
* pandas
* numpy

---

## 📁 Project Structure

```
CropAI/
│
├── app.py                  # Flask backend
├── train_model.py          # Model training script
├── models/                 # Saved ML models & data
│   ├── rf_model.pkl
│   ├── lr_model.pkl
│   ├── meta.json
│   ├── state_districts.json
│
├── templates/              # HTML pages
│   ├── predict.html
│   ├── recommend.html
│   ├── dashboard.html
│   ├── compare.html
│   ├── forecast.html
│
├── static/
│   ├── css/
│   ├── js/
│
└── BDA DATASET.xlsx
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository

```
git clone https://github.com/your-username/cropai.git
cd cropai
```

---

### 2️⃣ Install Dependencies

```
pip install -r requirements.txt
```

---

### 3️⃣ Train Model

```
python train_model.py
```

---

### 4️⃣ Run Application

```
python app.py
```

---

### 5️⃣ Open in Browser

```
http://127.0.0.1:5000
```

---

## 🔄 Working Flow

```
User Input → Frontend → API Call → Flask Backend → ML Model → Prediction → JSON Response → UI Display
```

---

## 📊 APIs Used

| API              | Purpose                   |
| ---------------- | ------------------------- |
| `/api/predict`   | Predict crop production   |
| `/api/recommend` | Recommend crops           |
| `/api/dashboard` | Provide chart data        |
| `/api/compare`   | Compare ML models         |
| `/api/forecast`  | Predict future production |

---

## 💡 Key Highlights

* Full-stack ML application
* Real-time predictions
* Data visualization dashboard
* Model comparison system
* Forecasting with confidence interval

---

## ⚠️ Limitations

* Uses historical dataset (no real-time data)
* Forecasting uses simple trend method
* Accuracy depends on dataset quality

---

## 🚀 Future Improvements

* Add weather API integration
* Use advanced time-series models (ARIMA, LSTM)
* Improve recommendation accuracy
* Deploy on cloud

---

## 👨‍💻 Author

**Aditi Avhad**
B.Tech (Data Science / IT)

---

## ⭐ Conclusion

CropAI is a smart agriculture analytics system that helps users make data-driven decisions using machine learning, visualization, and forecasting.

---
