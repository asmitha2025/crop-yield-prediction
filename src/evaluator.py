"""
evaluator.py
============
Model evaluation metrics and SHAP explainability utilities.
"""

import logging
import numpy as np
import pandas as pd
from typing import Any, Dict, Optional

from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score,
)

logger = logging.getLogger(__name__)


def compute_metrics(
    model: Any,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    model_name: str = "",
) -> Dict[str, float]:
    """Compute regression metrics for a single model on the test set.

    Returns dict with keys: R2, MAE, RMSE, MSE, MAPE.
    """
    y_pred = model.predict(X_test)
    mse  = mean_squared_error(y_test, y_pred)
    mae  = mean_absolute_error(y_test, y_pred)
    r2   = r2_score(y_test, y_pred)
    rmse = np.sqrt(mse)
    # Mean Absolute Percentage Error (avoid div/0)
    mape = np.mean(np.abs((y_test - y_pred) / np.where(y_test == 0, 1, y_test))) * 100

    logger.info(
        "%s | R2=%.4f  MAE=%.4f  RMSE=%.4f  MAPE=%.2f%%",
        model_name, r2, mae, rmse, mape,
    )
    return {"R2": r2, "MAE": mae, "RMSE": rmse, "MSE": mse, "MAPE (%)": mape}


def compute_all_metrics(
    models: Dict[str, Any],
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> pd.DataFrame:
    """Compute metrics for all models and return a comparison DataFrame."""
    records = []
    for name, model in models.items():
        m = compute_metrics(model, X_test, y_test, model_name=name)
        m["Model"] = name
        records.append(m)
    return pd.DataFrame(records).set_index("Model")


def get_predictions(
    models: Dict[str, Any],
    X_test: pd.DataFrame,
) -> Dict[str, np.ndarray]:
    """Return predictions from all models as a dict."""
    return {name: model.predict(X_test) for name, model in models.items()}


def get_feature_importances(
    models: Dict[str, Any],
    feature_names: list,
) -> pd.DataFrame:
    """Return a wide DataFrame of feature importances for all models."""
    records = {}
    for name, model in models.items():
        if hasattr(model, "feature_importances_"):
            records[name] = model.feature_importances_
    df = pd.DataFrame(records, index=feature_names)
    return df


def build_shap_explainer(model: Any, X_train: pd.DataFrame):
    """Build and return a SHAP TreeExplainer for a tree-based model."""
    try:
        import shap
        explainer = shap.TreeExplainer(model)
        return explainer
    except Exception as e:
        logger.warning("SHAP explainer failed: %s", e)
        return None


def get_shap_values(explainer: Any, X: pd.DataFrame) -> Optional[np.ndarray]:
    """Return SHAP values for X using a pre-built explainer."""
    if explainer is None:
        return None
    try:
        return explainer.shap_values(X)
    except Exception as e:
        logger.warning("SHAP value computation failed: %s", e)
        return None
