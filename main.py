import io
import logging
import math
import pickle
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import shap
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from sklearn.model_selection import train_test_split

from src.data_loader import FEATURE_COLS, FEATURE_RANGES, YIELD_COL, get_features_target, load_data
from src.evaluator import compute_all_metrics
from src.model_trainer import get_best_model_name, train_all_models

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "crop yield data sheet.xlsx"
MODEL_PATH = BASE_DIR / "crop_yield_model.pkl"
METADATA_PATH = BASE_DIR / "model_metadata.pkl"

LOCATIONS = [
    "North Valley-12",
    "Delta Basin-A",
    "Highland-S",
    "North Valley-09",
    "Delta Basin-C",
    "Highland Plateau",
    "North Valley-03",
    "Delta Basin-W",
]

logger = logging.getLogger(__name__)

app = FastAPI(title="Precision Yield Intelligence")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

model: Any = None
explainer: Any = None
model_metadata: dict[str, Any] = {}
data_frame: pd.DataFrame | None = None


@app.on_event("startup")
def startup_event():
    load_runtime_state()


def load_runtime_state():
    global model, explainer, model_metadata, data_frame

    if MODEL_PATH.exists():
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        try:
            explainer = shap.TreeExplainer(model)
        except Exception as exc:
            explainer = None
            logger.warning("SHAP explainer initialization failed: %s", exc)
    else:
        logger.warning("Model file %s not found.", MODEL_PATH)

    if METADATA_PATH.exists():
        with open(METADATA_PATH, "rb") as f:
            model_metadata = pickle.load(f)

    if DATA_PATH.exists():
        data_frame = enrich_records(load_data(str(DATA_PATH)))
    else:
        logger.warning("Dataset file %s not found.", DATA_PATH)


class PredictionRequest(BaseModel):
    temperature: float = Field(..., ge=FEATURE_RANGES["Temperatue"][0], le=FEATURE_RANGES["Temperatue"][1])
    humidity: float = Field(..., ge=FEATURE_RANGES["Humidity (%)"][0], le=FEATURE_RANGES["Humidity (%)"][1])
    rainfall: float = Field(..., ge=FEATURE_RANGES["Rain Fall (mm)"][0], le=FEATURE_RANGES["Rain Fall (mm)"][1])
    nitrogen: float = Field(..., ge=FEATURE_RANGES["Nitrogen (N)"][0], le=FEATURE_RANGES["Nitrogen (N)"][1])
    phosphorus: float = Field(..., ge=FEATURE_RANGES["Phosphorus (P)"][0], le=FEATURE_RANGES["Phosphorus (P)"][1])
    potassium: float = Field(..., ge=FEATURE_RANGES["Potassium (K)"][0], le=FEATURE_RANGES["Potassium (K)"][1])
    ph_value: float = Field(..., ge=FEATURE_RANGES["pH Value"][0], le=FEATURE_RANGES["pH Value"][1])
    fertilizer: float = Field(..., ge=FEATURE_RANGES["Fertilizer"][0], le=FEATURE_RANGES["Fertilizer"][1])


def enrich_records(df: pd.DataFrame) -> pd.DataFrame:
    enriched = df.reset_index(drop=True).copy()
    enriched["Record ID"] = [f"CY-{i + 1:04d}" for i in range(len(enriched))]
    enriched["Location"] = [LOCATIONS[i % len(LOCATIONS)] for i in range(len(enriched))]
    dates = pd.date_range(end=pd.Timestamp.now().floor("min"), periods=len(enriched), freq="h")
    enriched["Sample Date"] = dates.strftime("%b %d, %Y")
    enriched["Sample Time"] = dates.strftime("%H:%M")
    return enriched


def require_data() -> pd.DataFrame:
    if data_frame is None:
        raise HTTPException(status_code=503, detail="Dataset not loaded")
    return data_frame.copy()


def require_model():
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return model


def build_feature_frame(data: PredictionRequest) -> pd.DataFrame:
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
    return pd.DataFrame([input_dict], columns=FEATURE_COLS)


def to_json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: to_json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [to_json_safe(item) for item in value]
    if isinstance(value, np.generic):
        return to_json_safe(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def metric_value(name: str, default: float = 0.0) -> float:
    test_metrics = model_metadata.get("test_metrics", {})
    cv_metrics = model_metadata.get("cv_metrics", {})
    return float(test_metrics.get(name, cv_metrics.get(name, default)) or default)


def filtered_records(
    search: str = "",
    ph_min: float | None = None,
    ph_max: float | None = None,
    location: str | None = None,
    sort: str = "id",
    order: str = "asc",
) -> pd.DataFrame:
    df = require_data()

    if ph_min is not None:
        df = df[df["pH Value"] >= ph_min]
    if ph_max is not None:
        df = df[df["pH Value"] <= ph_max]
    if location:
        allowed = {item.strip() for item in location.split(",") if item.strip()}
        if allowed:
            df = df[df["Location"].isin(allowed)]

    query = search.strip().lower()
    if query:
        haystack = (
            df["Record ID"].astype(str)
            + " "
            + df["Location"].astype(str)
            + " "
            + df["pH Value"].round(2).astype(str)
            + " "
            + df[YIELD_COL].round(2).astype(str)
        ).str.lower()
        df = df[haystack.str.contains(query, regex=False)]

    sort_map = {
        "id": "Record ID",
        "date": "Record ID",
        "location": "Location",
        "ph": "pH Value",
        "moisture": "Humidity (%)",
        "temp": "Temperatue",
        "yield": YIELD_COL,
    }
    sort_col = sort_map.get(sort, "Record ID")
    return df.sort_values(sort_col, ascending=order != "desc")


def serialize_record(row: pd.Series) -> dict[str, Any]:
    yield_value = float(row[YIELD_COL])
    status = "High Yield"
    if row["pH Value"] < 5.5 or row["pH Value"] > 7.8:
        status = "pH Watch"
    elif yield_value < 30:
        status = "Low Yield"

    return {
        "id": row["Record ID"],
        "date": row["Sample Date"],
        "time": row["Sample Time"],
        "location": row["Location"],
        "ph": round(float(row["pH Value"]), 2),
        "moisture": round(float(row["Humidity (%)"]), 1),
        "temperature": round(float(row["Temperatue"]), 1),
        "rainfall": round(float(row["Rain Fall (mm)"]), 1),
        "nitrogen": round(float(row["Nitrogen (N)"]), 1),
        "phosphorus": round(float(row["Phosphorus (P)"]), 1),
        "potassium": round(float(row["Potassium (K)"]), 1),
        "fertilizer": round(float(row["Fertilizer"]), 1),
        "yield": round(yield_value, 2),
        "status": status,
    }


def make_metadata(best_name: str, best_model: Any, cv_df: pd.DataFrame, metrics_df: pd.DataFrame, y: pd.Series, train_len: int, test_len: int):
    return {
        "model_name": best_name,
        "model_type": type(best_model).__name__,
        "model_params": to_json_safe(best_model.get_params()),
        "training_date": datetime.now().isoformat(timespec="seconds"),
        "cv_metrics": to_json_safe(cv_df.loc[best_name].to_dict()),
        "test_metrics": to_json_safe(metrics_df.loc[best_name].to_dict()),
        "features": FEATURE_COLS,
        "target": YIELD_COL,
        "target_min": float(y.min()),
        "target_max": float(y.max()),
        "training_samples": int(train_len),
        "test_samples": int(test_len),
    }


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


@app.get("/api/health")
async def health():
    return {
        "status": "ok" if model is not None and data_frame is not None else "degraded",
        "model_loaded": model is not None,
        "dataset_loaded": data_frame is not None,
        "explainer_loaded": explainer is not None,
        "model_type": type(model).__name__ if model is not None else None,
        "metadata": to_json_safe(model_metadata),
        "features": FEATURE_COLS,
    }


@app.get("/api/dashboard")
async def dashboard_data():
    df = require_data()
    y = df[YIELD_COL]
    accuracy = metric_value("R2", metric_value("CV R2 (mean)", 0.0))
    target_max = float(model_metadata.get("target_max") or y.max())

    trend = []
    boundaries = np.linspace(0, len(df), 13, dtype=int)
    for i in range(12):
        chunk = df.iloc[boundaries[i] : boundaries[i + 1]]
        trend.append({"label": f"B{i + 1}", "yield": round(float(chunk[YIELD_COL].mean()), 2)})

    anomalies = df.assign(ph_gap=(df["pH Value"] - 6.5).abs()).nlargest(3, "ph_gap")

    return {
        "total_samples": int(len(df)),
        "average_yield": round(float(y.mean()), 2),
        "yield_target_percent": round(float(y.mean() / target_max * 100), 1) if target_max else 0,
        "model_accuracy": round(accuracy * 100, 1),
        "model_name": model_metadata.get("model_name", type(model).__name__ if model is not None else "Unknown"),
        "training_date": model_metadata.get("training_date", "Unknown"),
        "summary": {
            "temperature": round(float(df["Temperatue"].mean()), 1),
            "humidity": round(float(df["Humidity (%)"].mean()), 1),
            "rainfall": round(float(df["Rain Fall (mm)"].mean()), 1),
            "median_yield": round(float(y.median()), 2),
        },
        "trend": trend,
        "anomalies": [serialize_record(row) for _, row in anomalies.iterrows()],
        "locations": sorted(df["Location"].unique().tolist()),
    }


@app.get("/api/insights")
async def insights_data():
    df = require_data()
    current_model = require_model()

    importance = []
    if hasattr(current_model, "feature_importances_"):
        pairs = zip(FEATURE_COLS, current_model.feature_importances_)
        importance = [
            {"feature": feature, "importance": round(float(score), 5)}
            for feature, score in sorted(pairs, key=lambda item: item[1], reverse=True)
        ]

    corr = df[FEATURE_COLS + [YIELD_COL]].corr(numeric_only=True)[YIELD_COL].drop(YIELD_COL)
    correlations = [
        {"feature": feature, "correlation": round(float(value), 4)}
        for feature, value in corr.reindex(corr.abs().sort_values(ascending=False).index).items()
    ]

    sample = df.head(24)
    predictions = current_model.predict(sample[FEATURE_COLS])
    accuracy_track = [
        {
            "id": row["Record ID"],
            "actual": round(float(row[YIELD_COL]), 2),
            "predicted": round(float(pred), 2),
        }
        for (_, row), pred in zip(sample.iterrows(), predictions)
    ]

    return {
        "model_name": model_metadata.get("model_name", type(current_model).__name__),
        "model_type": type(current_model).__name__,
        "training_date": model_metadata.get("training_date", "Unknown"),
        "metrics": {
            "r2": round(metric_value("R2", metric_value("CV R2 (mean)", 0.0)), 4),
            "rmse": round(metric_value("RMSE", 0.0), 4),
            "mae": round(metric_value("MAE", 0.0), 4),
            "mape": round(metric_value("MAPE (%)", 0.0), 2),
        },
        "feature_importance": importance,
        "correlations": correlations,
        "accuracy_track": accuracy_track,
    }


@app.get("/api/records")
async def records(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: str = "",
    ph_min: float | None = None,
    ph_max: float | None = None,
    location: str | None = None,
    sort: str = "id",
    order: str = "asc",
):
    df = filtered_records(search=search, ph_min=ph_min, ph_max=ph_max, location=location, sort=sort, order=order)
    page = df.iloc[offset : offset + limit]
    return {
        "total": int(len(df)),
        "offset": offset,
        "limit": limit,
        "records": [serialize_record(row) for _, row in page.iterrows()],
        "locations": sorted(require_data()["Location"].unique().tolist()),
        "summary": {
            "average_yield": round(float(df[YIELD_COL].mean()), 2) if len(df) else 0,
            "average_ph": round(float(df["pH Value"].mean()), 2) if len(df) else 0,
        },
    }


@app.get("/api/export.csv")
async def export_csv(search: str = "", ph_min: float | None = None, ph_max: float | None = None, location: str | None = None):
    df = filtered_records(search=search, ph_min=ph_min, ph_max=ph_max, location=location)
    export_cols = ["Record ID", "Sample Date", "Sample Time", "Location", *FEATURE_COLS, YIELD_COL]
    buffer = io.StringIO()
    df[export_cols].to_csv(buffer, index=False)
    return Response(
        buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="crop-yield-records.csv"'},
    )


@app.get("/api/report")
async def report():
    insights = await insights_data()
    dashboard_summary = await dashboard_data()
    text = "\n".join(
        [
            "Crop Yield Model Report",
            f"Generated: {datetime.now().isoformat(timespec='seconds')}",
            f"Model: {insights['model_name']} ({insights['model_type']})",
            f"Samples: {dashboard_summary['total_samples']}",
            f"Average yield: {dashboard_summary['average_yield']} Q/ac",
            f"R2: {insights['metrics']['r2']}",
            f"RMSE: {insights['metrics']['rmse']}",
            f"MAE: {insights['metrics']['mae']}",
            "",
            "Top feature importances:",
            *[
                f"- {item['feature']}: {item['importance']}"
                for item in insights["feature_importance"][:5]
            ],
        ]
    )
    return Response(
        text,
        media_type="text/plain",
        headers={"Content-Disposition": 'attachment; filename="crop-yield-model-report.txt"'},
    )


@app.post("/api/retrain")
async def retrain():
    global model, explainer, model_metadata, data_frame

    df = load_data(str(DATA_PATH))
    X, y = get_features_target(df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    models, cv_df = train_all_models(X_train, y_train)
    metrics_df = compute_all_metrics(models, X_test, y_test)
    best_name = get_best_model_name(cv_df)
    best_model = models[best_name]

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(best_model, f)

    model_metadata = make_metadata(best_name, best_model, cv_df, metrics_df, y, len(X_train), len(X_test))
    with open(METADATA_PATH, "wb") as f:
        pickle.dump(model_metadata, f)

    model = best_model
    data_frame = enrich_records(df)
    try:
        explainer = shap.TreeExplainer(model)
    except Exception as exc:
        explainer = None
        logger.warning("SHAP explainer initialization failed after retrain: %s", exc)

    return {"status": "retrained", "metadata": to_json_safe(model_metadata)}


@app.post("/api/predict")
async def predict(data: PredictionRequest):
    current_model = require_model()

    input_df = build_feature_frame(data)
    try:
        raw_prediction = float(current_model.predict(input_df)[0])
        prediction = max(0.0, raw_prediction)

        shap_data = {}
        if explainer is not None:
            try:
                sv = explainer.shap_values(input_df)
                if isinstance(sv, list):
                    sv = sv[0]
                if len(sv.shape) > 1:
                    sv = sv[0]

                for i, col in enumerate(FEATURE_COLS):
                    shap_data[col] = float(sv[i])
            except Exception as exc:
                logger.warning("Error calculating SHAP values: %s", exc)

        return {
            "prediction": prediction,
            "raw_prediction": raw_prediction,
            "shap_values": shap_data,
        }
    except Exception as exc:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
