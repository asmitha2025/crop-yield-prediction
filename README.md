---
title: Crop Yield Prediction
emoji: 🌾
colorFrom: green
colorTo: blue
sdk: docker
pinned: false
---

# Emerald Horizon: Controlled-Environment Crop Yield Intelligence

Emerald Horizon is a state-of-the-art controlled-environment agriculture analytics platform. Designed as a recruiters' showcase, it blends high-fidelity machine learning pipeline engineering with an ultra-premium, dark-themed dashboard. 

The application utilizes **FastAPI** to back JSON API endpoints and render server-side pages via **Jinja2 templates**, fully styled with a responsive design using **Tailwind CSS v4** and customized glassmorphic card surfaces.

---

## 🚀 The Stack & Core Technology

- **Backend Framework:** [FastAPI](https://fastapi.tiangolo.com/) – high-performance, asynchronous routing with robust Pydantic data validation schemas.
- **Frontend & Rendering:** [Jinja2 Templates](https://jinja.palletsprojects.com/) & [Tailwind CSS v4](https://tailwindcss.com/) – creating a high-contrast editorial look concepted as "The Synthetic Greenhouse" (glassmorphism, vibrant soil/nature color palettes, zero rigid layout dividing lines).
- **Explainable AI:** [SHAP (SHapley Additive exPlanations)](https://github.com/shap/shap) – TreeExplainer integration to extract hyper-local feature attribution details for each generated yield forecast.
- **Machine Learning Pipeline:** [Scikit-learn](https://scikit-learn.org/) & [XGBoost](https://xgboost.readthedocs.io/) – comparisons across Decision Trees, Random Forests, Gradient Boosting, and Extreme Gradient Boosting Regressors with automated 5-Fold Cross-Validation selection.

---

## 📱 Interactive Agronomy Pages

Emerald Horizon delivers a complete, professional agronomic platform across four dynamic pages:

1. **Dashboard:** Live model health cards, sample totals, geographic agricultural yield trends, and automated reservoir pH anomaly highlighting.
2. **Yield Predictor:** Simulate harvests interactively. Submit climate variables (Temperature, Humidity, Rain Fall) and soil nutrient levels (N, P, K, pH) through form elements to receive real-time predictions with custom **SHAP** feature contribution attribution feedback.
3. **Model Insights:** Recruiter-ready data science deep dive containing holdout test scores ($R^2$, RMSE, MAE, MAPE), interactive feature importance lists, variable correlation matrix, and an actual-vs-predicted harvest tracking timeline.
4. **Data Explorer:** An elegant grid to navigate granular records. Filter by location or pH range, execute real-time searches across raw sensor logs, and export raw data to CSV or download full model reports.

---

## 🛠️ Data Features & Features Matrix

The predictive models are trained on rich environmental feature sets:
- `Nitrogen (N)` (kg/ha)
- `Phosphorus (P)` (kg/ha)
- `Potassium (K)` (kg/ha)
- `Temperatue` (degrees C - preserving source dataset typo)
- `Humidity (%)`
- `pH Value`
- `Rain Fall (mm)`
- `Fertilizer` (kg/ha)

**Target Variable:**
- `Yeild (Q/acre)` (Quintals per acre - preserving source dataset typo)

---

## ⚙️ Seamless Setup & Installation

Follow these steps to generate the dataset, train the predictive models, compile the style sheets, and run the FastAPI server:

### 1. Create and Activate a Python Environment
```bash
python -m venv venv
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies
Install the required machine learning, web server, and styling dev dependencies:
```bash
pip install -r requirements.txt
npm install
```

### 3. Generate the Dataset
Create the synthetic agricultural dataset. This script generates 1,000 realistic agricultural observations with non-linear environmental relationships and realistic anomalies, saving them to a spreadsheet:
```bash
python generate_dataset.py
```

### 4. Train the Model Pipeline
Execute the machine learning pipeline. This loads the generated Excel data, splits it into training/holdout sets, evaluates four competitive tree-based regression models using 5-fold cross validation, and serializes the best performing model and its metadata:
```bash
python crop_yield_prediction.py
```
*Outputs generated:* `crop_yield_model.pkl` and `model_metadata.pkl`.

### 5. Compile Tailwind CSS Output
Build the compiled CSS files using the Tailwind CLI:
```bash
npm run build:css
```

### 6. Run the FastAPI Development Server
Start the uvicorn development server:
```bash
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
Open your browser and navigate to: **`http://127.0.0.1:8000`**

---

## 🔌 API Endpoints Reference

The FastAPI backend exposes a clean JSON API for consumption by the Jinja templates and external clients:
- `GET /api/health` – System status, model loading checks, and hyperparameter metadata.
- `GET /api/dashboard` – Summarized averages, yield targets, anomaly lists, and active greenhouse sectors.
- `GET /api/insights` – Model metrics, computed feature importances, feature correlation metrics, and comparison metrics.
- `GET /api/records` – Searchable, filterable, and paginated dataset logs.
- `GET /api/export.csv` – Generate and stream the filtered dataset as a CSV file.
- `GET /api/report` – Download a plain-text evaluation report containing core metrics and top feature attributions.
- `POST /api/predict` – Submits soil and climate parameters to calculate predicted yield along with **SHAP** attributions.
- `POST /api/retrain` – Automatically triggers a pipeline execution on the current dataset to search for the best model and refresh the serialized files.
