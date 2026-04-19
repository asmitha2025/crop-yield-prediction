import os
import pickle
import pandas as pd
import shap
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from src.data_loader import FEATURE_COLS

app = FastAPI(title="Precision Yield Intelligence")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

MODEL_PATH = "crop_yield_model.pkl"
model = None
explainer = None

@app.on_event("startup")
def startup_event():
    global model, explainer
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        try:
            # TreeExplainer is fast for tree-based models (XGBoost, RF, etc.)
            explainer = shap.TreeExplainer(model)
        except Exception as e:
            print(f"Warning: SHAP Explainer initialization failed: {e}")
    else:
        print(f"Warning: Model file {MODEL_PATH} not found.")

class PredictionRequest(BaseModel):
    temperature: float
    humidity: float
    rainfall: float
    nitrogen: float
    phosphorus: float
    potassium: float
    ph_value: float
    fertilizer: float

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/predictor", response_class=HTMLResponse)
async def predictor(request: Request):
    return templates.TemplateResponse("predictor.html", {"request": request})

@app.get("/insights", response_class=HTMLResponse)
async def insights(request: Request):
    return templates.TemplateResponse("insights.html", {"request": request})

@app.get("/explorer", response_class=HTMLResponse)
async def explorer(request: Request):
    return templates.TemplateResponse("explorer.html", {"request": request})

@app.post("/api/predict")
async def predict(data: PredictionRequest):
    if not model:
        return {"error": "Model not loaded", "prediction": None, "shap_values": {}}
    
    input_dict = {
        "Nitrogen (N)": data.nitrogen,
        "Phosphorus (P)": data.phosphorus,
        "Potassium (K)": data.potassium,
        "Temperatue": data.temperature,
        "Humidity (%)": data.humidity,
        "pH Value": data.ph_value,
        "Rain Fall (mm)": data.rainfall,
        "Fertilizer": data.fertilizer,
    }
    
    input_df = pd.DataFrame([input_dict])[FEATURE_COLS]
    try:
        pred = model.predict(input_df)[0]
        
        # Calculate SHAP values
        shap_data = {}
        if explainer:
            try:
                sv = explainer.shap_values(input_df)
                # Handle different SHAP output formats
                if isinstance(sv, list): sv = sv[0]
                if len(sv.shape) > 1: sv = sv[0]
                
                for i, col in enumerate(FEATURE_COLS):
                    shap_data[col] = float(sv[i])
            except Exception as e:
                print(f"Error calculating SHAP values: {e}")
        
        return {
            "prediction": float(pred),
            "shap_values": shap_data
        }
    except Exception as e:
        return {"error": str(e), "prediction": None, "shap_values": {}}
