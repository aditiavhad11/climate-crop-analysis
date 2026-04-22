import pandas as pd
import numpy as np
import pickle
import json
import os

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error

# =========================
# LOAD DATA
# =========================
df = pd.read_excel("BDA DATASET.xlsx")

# Clean column names
df.columns = df.columns.str.strip()
df["Season"] = df["Season"].str.strip()

# =========================
# FEATURE ENGINEERING
# =========================
months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
df["Rainfall"] = df[months].sum(axis=1)

# Remove invalid data
df = df.dropna(subset=["Production","Area","Rainfall"])
df = df[df["Production"] > 0]
df = df[df["Area"] > 0]

# Interaction feature
df["Rainfall_Area"] = df["Rainfall"] * df["Area"]

# Log transformation (boosts performance)
df["Log_Production"] = np.log1p(df["Production"])
df["Log_Area"] = np.log1p(df["Area"])
df["Log_Rainfall_Area"] = np.log1p(df["Rainfall_Area"])

# =========================
# ENCODING
# =========================
le_state = LabelEncoder()
le_district = LabelEncoder()
le_season = LabelEncoder()
le_crop = LabelEncoder()

df["State_enc"] = le_state.fit_transform(df["State_Name"])
df["District_enc"] = le_district.fit_transform(df["District_Name"])
df["Season_enc"] = le_season.fit_transform(df["Season"])
df["Crop_enc"] = le_crop.fit_transform(df["Crop"])

# =========================
# FEATURES
# =========================
features = [
    "Crop_enc",
    "Season_enc",
    "Rainfall",
    "Log_Area",
    "Log_Rainfall_Area",
    "State_enc",
    "District_enc"
]

X = df[features]
y = df["Log_Production"]

# =========================
# SPLIT DATA
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# =========================
# MODELS
# =========================
rf = RandomForestRegressor(
    n_estimators=300,
    max_depth=25,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

lr = LinearRegression()

# Train
rf.fit(X_train, y_train)
lr.fit(X_train, y_train)

# =========================
# EVALUATION
# =========================
rf_pred = rf.predict(X_test)
lr_pred = lr.predict(X_test)

rf_r2 = r2_score(y_test, rf_pred)
rf_mse = mean_squared_error(y_test, rf_pred)
rf_rmse = np.sqrt(rf_mse)

lr_r2 = r2_score(y_test, lr_pred)
lr_mse = mean_squared_error(y_test, lr_pred)
lr_rmse = np.sqrt(lr_mse)

print(f"RF R2: {rf_r2:.4f} | RMSE: {rf_rmse:.4f}")
print(f"LR R2: {lr_r2:.4f} | RMSE: {lr_rmse:.4f}")

# =========================
# SAVE MODELS
# =========================
os.makedirs("models", exist_ok=True)

pickle.dump(rf, open("models/rf_model.pkl", "wb"))
pickle.dump(lr, open("models/lr_model.pkl", "wb"))

pickle.dump(le_state, open("models/le_state.pkl", "wb"))
pickle.dump(le_district, open("models/le_district.pkl", "wb"))
pickle.dump(le_season, open("models/le_season.pkl", "wb"))
pickle.dump(le_crop, open("models/le_crop.pkl", "wb"))

# =========================
# META DATA
# =========================
meta = {
    "states": sorted(df["State_Name"].unique().tolist()),
    "crops": sorted(df["Crop"].unique().tolist()),
    "seasons": sorted(df["Season"].unique().tolist()),

    "rf_r2": round(rf_r2, 4),
    "rf_mse": round(rf_mse, 4),
    "rf_rmse": round(rf_rmse, 4),

    "lr_r2": round(lr_r2, 4),
    "lr_mse": round(lr_mse, 4),
    "lr_rmse": round(lr_rmse, 4),

    "use_log": True
}

json.dump(meta, open("models/meta.json", "w"))

# =========================
# STATE → DISTRICT MAP
# =========================
state_districts = (
    df.groupby("State_Name")["District_Name"]
    .unique()
    .apply(list)
    .to_dict()
)

json.dump(state_districts, open("models/state_districts.json", "w"))

# =========================
# DASHBOARD DATA
# =========================
crop_state = df.groupby(["State_Name","Crop"])["Production"].mean().reset_index()
crop_state.to_json("models/crop_state_agg.json", orient="records")

# =========================
# FORECAST DATA
# =========================
year_trend = df.groupby(["Crop_Year","Crop","State_Name"])["Production"].mean().reset_index()
year_trend.to_json("models/year_trend.json", orient="records")
