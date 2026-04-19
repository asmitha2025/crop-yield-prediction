# 🌾 Crop Yield Prediction API & Web Dashboard

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

An end-to-end Machine Learning pipeline that predicts agricultural crop yield based on environmental and soil conditions. This project features multiple machine learning models (XGBoost, Gradient Boosting, Random Forest, Decision Tree), an interactive web dashboard for real-time predictions, and **SHAP** (SHapley Additive exPlanations) for model explainability.

## 🚀 Features

- **Advanced ML Models**: Compares XGBoost, Gradient Boosting Regressor, Random Forest, and Decision Trees using 5-fold cross-validation.
- **Interactive Dashboard**: A full-fledged Streamlit web app with 4 pages (Data Explorer, Model Training, Predictor, and Insights).
- **Explainable AI (XAI)**: Uses SHAP values to explain individual predictions in a waterfall chart, answering *why* a model made a specific prediction.
- **Robust Pipeline**: Includes missing value imputation, proper metric tracking (R², RMSE, MAE, MAPE), and modular clean code architecture.

## 📊 Dataset

The dataset includes the following features:
- **Soil Nutrients**: Nitrogen (N), Phosphorus (P), Potassium (K) (in kg/ha)
- **Environment**: Temperature (°C), Humidity (%), Rain Fall (mm)
- **Soil Status**: pH Value, Fertilizer (kg/ha)
- **Target Variable**: Crop Yield (Quintals/acre)

*(Includes a realistic synthetic data generator script `generate_dataset.py` for testing).*

## 🛠️ Tech Stack

- **Data Processing**: `pandas`, `numpy`
- **Machine Learning**: `scikit-learn`, `xgboost`
- **Model Explainability**: `shap`
- **Visualization**: `matplotlib`, `seaborn`, `plotly`
- **Web Application**: `streamlit`

## 💻 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/crop-yield-prediction.git
cd crop-yield-prediction
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

3. Generate the synthetic dataset (if `crop yield data sheet.xlsx` is not present):
```bash
python generate_dataset.py
```

## 🏃‍♂️ Usage

### 1. Web Dashboard (Recommended)
Launch the interactive Streamlit dashboard:
```bash
streamlit run app.py
```
This will open a local web server (typically `http://localhost:8501`).

### 2. Command Line Interface (CLI)
Run the automated pipeline to train models and output metrics to the console:
```bash
python crop_yield_prediction.py
```

## 📈 Model Performance Highlights
*Sample metrics using 5-fold Cross-Validation*

| Model | R² Score | RMSE |
|-------|----------|------|
| **XGBoost** | `~0.98` | `~1.2` |
| **Gradient Boosting** | `~0.96` | `~2.4` |
| **Random Forest** | `~0.95` | `~3.0` |
| **Decision Tree** | `~0.92` | `~3.8` |

*(Actual metrics vary based on random seed and dataset generation)*

## 📄 License
This project is licensed under the MIT License.
