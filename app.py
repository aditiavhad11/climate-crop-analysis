from flask import Flask, render_template, request, jsonify
import numpy as np
import pickle
import json
import os
import pandas as pd   

app = Flask(__name__)

# =========================
# BASE PATH
# =========================
BASE = os.path.dirname(os.path.abspath(__file__))

def load_model(name):
    path = os.path.join(BASE, "models", name)
    print("Loading:", path)
    with open(path, "rb") as f:
        return pickle.load(f)

# =========================
# LOAD MODEL
# =========================
rf = load_model("rf_model.pkl")
lr = load_model("lr_model.pkl")   
le_state = load_model("le_state.pkl")
le_district = load_model("le_district.pkl")
le_season = load_model("le_season.pkl")
le_crop = load_model("le_crop.pkl")

# =========================
# LOAD META
# =========================
with open(os.path.join(BASE, "models", "meta.json")) as f:
    meta = json.load(f)

with open(os.path.join(BASE, "models", "state_districts.json")) as f:
    STATE_DISTRICTS = json.load(f)

# LOAD DATASET (for dashboard + forecast FIX)
df = pd.read_excel(os.path.join(BASE, "BDA DATASET.xlsx"))
df.columns = df.columns.str.strip()

# =========================
# HELPERS
# =========================
def safe_encode(le, value):
    try:
        return le.transform([value])[0]
    except:
        return 0

def make_features(crop, season, rainfall, area, state, district):
    rainfall = float(rainfall)
    area = float(area)

    rainfall_area = rainfall * area

    return [[
        safe_encode(le_crop, crop),
        safe_encode(le_season, season),
        rainfall,
        np.log1p(area),
        np.log1p(rainfall_area),
        safe_encode(le_state, state),
        safe_encode(le_district, district),
    ]]

# =========================
# ROUTES
# =========================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict")
def predict_page():
    return render_template(
        "predict.html",
        crops=meta["crops"],
        seasons=meta["seasons"]
    )

@app.route("/recommend")
def recommend_page():
    return render_template(
        "recommend.html",
        states=meta["states"],
        state_districts=STATE_DISTRICTS
    )

@app.route("/compare")
def compare_page():
    return render_template(
        "compare.html",
        crops=meta["crops"],
        meta=meta
    )

@app.route("/forecast")
def forecast_page():
    return render_template(
        "forecast.html",
        crops=meta["crops"],
        states=meta["states"]
    )

@app.route("/dashboard")
def dashboard_page():
    return render_template(
        "dashboard.html",
        states=meta["states"]
    )

# =========================
# API: PREDICT (UNCHANGED)
# =========================
@app.route("/api/predict", methods=["POST"])
def api_predict():
    try:
        data = request.json

        feats = make_features(
            data["crop"],
            data["season"],
            data["rainfall"],
            data["area"],
            data.get("state", meta["states"][0]),
            data.get("district", STATE_DISTRICTS.get(meta["states"][0], [""])[0])
        )

        log_pred = rf.predict(feats)[0]
        production = np.expm1(log_pred)

        return jsonify({
            "production": round(float(production), 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)})

# =========================
# API: RECOMMEND (FIXED)
# =========================
@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    try:
        data = request.json

        state = data["state"]
        district = data["district"]
        rainfall = float(data["rainfall"])
        area = float(data["area"])

        results = []

        # =========================
        # STEP 1: FILTER BY DISTRICT (BEST)
        # =========================
        df_local = df[
            (df["State_Name"] == state) &
            (df["District_Name"] == district)
        ]

        # fallback if district empty
        if df_local.empty:
            df_local = df[df["State_Name"] == state]

        # =========================
        # STEP 2: GET TOP CROPS (REAL DATA)
        # =========================
        crop_stats = (
            df_local.groupby("Crop")["Production"]
            .mean()
            .sort_values(ascending=False)
        )

        # take top realistic crops
        possible_crops = crop_stats.head(10).index.tolist()

        # =========================
        # STEP 3: SEASON LOGIC
        # =========================
        if rainfall > 800:
            season = "Kharif"
        elif rainfall > 400:
            season = "Rabi"
        else:
            season = "Summer"

        # =========================
        # STEP 4: ML PREDICTION
        # =========================
        for crop in possible_crops:

            feats = make_features(
                crop, season, rainfall, area, state, district
            )

            pred = rf.predict(feats)[0]
            prod = float(np.expm1(pred))

            # Combine ML + real data importance
            real_score = crop_stats.get(crop, 1)

            final_score = prod * 0.7 + real_score * 0.3

            results.append({
                "crop": crop,
                "production": prod,
                "score": final_score
            })

        # =========================
        # STEP 5: FINAL RANKING
        # =========================
        results = sorted(results, key=lambda x: x["score"], reverse=True)[:5]

        max_val = results[0]["score"]

        for r in results:
            r["yield"] = round(r["production"], 2)
            r["percentage"] = round((r["score"] / max_val) * 100, 1)

        return jsonify({"recommendations": results})

    except Exception as e:
        print("SMART RECOMM ERROR:", e)
        return jsonify({"recommendations": []})
# =========================
# API: DASHBOARD 
# =========================
@app.route("/api/dashboard", methods=["POST"])
def api_dashboard():
    try:
        data = request.json
        state = data["state"]

        df_state = df[df["State_Name"].str.lower() == state.lower()]

        crop_data = (
            df_state.groupby("Crop")["Production"]
            .mean()
            .sort_values(ascending=False)
            .head(8)
        )

        return jsonify({
            "crop_production": {k: round(v, 2) for k, v in crop_data.items()}
        })

    except Exception as e:
        return jsonify({"error": str(e)})

# =========================
# API: COMPARE 
# =========================
@app.route("/api/compare", methods=["POST"])
def api_compare():
    try:
        data = request.json

        feats = make_features(
            data["crop"],
            meta["seasons"][0],
            data["rainfall"],
            data["area"],
            meta["states"][0],
            STATE_DISTRICTS.get(meta["states"][0], [""])[0]
        )

        # RF prediction
        rf_pred = np.expm1(rf.predict(feats)[0])

        # LR prediction
        lr_pred = np.expm1(lr.predict(feats)[0])

        return jsonify({
            "rf": {
                "mse": meta.get("rf_mse", 0.1),
                "r2": meta.get("rf_r2", 0.9),
                "prediction": round(float(rf_pred), 2)
            },
            "lr": {
                "mse": meta.get("lr_mse", 0.2),
                "r2": meta.get("lr_r2", 0.8),
                "prediction": round(float(lr_pred), 2)
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)})
# =========================
# API: FORECAST (FIXED)
# =========================
@app.route("/api/forecast", methods=["POST"])
def api_forecast():
    try:
        data = request.json

        crop = data.get("crop")
        state = data.get("state")
        years_ahead = int(data.get("years_ahead", 3))  

        # FILTER DATA
        df_filtered = df[
            (df["Crop"] == crop) &
            (df["State_Name"] == state)
        ]

        yearly = df_filtered.groupby("Crop_Year")["Production"].mean().reset_index()

        if yearly.empty:
            return jsonify({"error": "No data found"})

        # SORT YEARS
        yearly = yearly.sort_values("Crop_Year")

        years = yearly["Crop_Year"].tolist()
        values = yearly["Production"].tolist()

        # LAST YEAR FROM DATA (IMPORTANT)
        last_year = int(years[-1])

        # TREND CALCULATION
        if len(values) > 1:
            growth = np.mean(np.diff(values))
        else:
            growth = values[0] * 0.05  # fallback

        # =========================
        # FUTURE PREDICTION
        # =========================
        forecast = []
        current_val = values[-1]

        for i in range(1, years_ahead + 1):
            next_year = last_year + i
            pred = current_val + growth * i

            forecast.append({
                "year": next_year,
                "production": round(pred, 2),
                "upper": round(pred * 1.1, 2),
                "lower": round(pred * 0.9, 2)
            })

        # =========================
        # RETURN
        # =========================
        return jsonify({
            "historical": [
                {"year": int(y), "production": float(v)}
                for y, v in zip(years, values)
            ],
            "forecast": forecast,
            "current_year": last_year
        })

    except Exception as e:
        return jsonify({"error": str(e)})
# =========================
# API: DISTRICTS (UNCHANGED)
# =========================
@app.route("/api/districts/<state>")
def get_districts(state):
    return jsonify({
        "districts": STATE_DISTRICTS.get(state, [])
    })

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)