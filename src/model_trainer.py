"""
model_trainer.py
================
Trains Decision Tree, Random Forest, Gradient Boosting, and XGBoost regressors
with cross-validation. Returns trained model objects and CV metrics.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple

from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import cross_validate
import xgboost as xgb

logger = logging.getLogger(__name__)

# Best-practice hyperparameters (tuned offline via GridSearchCV)
MODEL_CONFIGS: Dict[str, Dict[str, Any]] = {
    "Decision Tree": {
        "model": DecisionTreeRegressor,
        "params": {
            "max_depth": 6,
            "min_samples_split": 4,
            "min_samples_leaf": 4,
            "random_state": 42,
        },
    },
    "Random Forest": {
        "model": RandomForestRegressor,
        "params": {
            "n_estimators": 200,
            "max_depth": 8,
            "min_samples_split": 4,
            "min_samples_leaf": 2,
            "random_state": 42,
            "n_jobs": None,
        },
    },
    "Gradient Boosting": {
        "model": GradientBoostingRegressor,
        "params": {
            "n_estimators": 200,
            "max_depth": 4,
            "learning_rate": 0.08,
            "subsample": 0.85,
            "random_state": 42,
        },
    },
    "XGBoost": {
        "model": xgb.XGBRegressor,
        "params": {
            "n_estimators": 200,
            "max_depth": 4,
            "learning_rate": 0.08,
            "subsample": 0.85,
            "colsample_bytree": 0.85,
            "random_state": 42,
            "verbosity": 0,
        },
    },
}


def train_all_models(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    cv_folds: int = 5,
) -> Tuple[Dict[str, Any], pd.DataFrame]:
    """Train all four models and collect cross-validation metrics.

    Args:
        X_train: Training features.
        y_train: Training target.
        cv_folds: Number of cross-validation folds.

    Returns:
        Tuple of:
          - trained_models: dict mapping model name to fitted estimator
          - cv_results_df: DataFrame with CV mean/std for each metric
    """
    trained_models: Dict[str, Any] = {}
    cv_records = []

    for name, cfg in MODEL_CONFIGS.items():
        logger.info("Training %s ...", name)
        estimator = cfg["model"](**cfg["params"])

        cv_scores = cross_validate(
            estimator,
            X_train,
            y_train,
            cv=cv_folds,
            scoring=["r2", "neg_mean_absolute_error", "neg_mean_squared_error"],
            return_train_score=True,
            n_jobs=None,
        )

        estimator.fit(X_train, y_train)
        trained_models[name] = estimator

        cv_records.append(
            {
                "Model": name,
                "CV R2 (mean)": np.mean(cv_scores["test_r2"]),
                "CV R2 (std)": np.std(cv_scores["test_r2"]),
                "CV MAE (mean)": -np.mean(cv_scores["test_neg_mean_absolute_error"]),
                "CV RMSE (mean)": np.sqrt(-np.mean(cv_scores["test_neg_mean_squared_error"])),
                "Train R2 (mean)": np.mean(cv_scores["train_r2"]),
            }
        )
        logger.info(
            "%s -> CV R2: %.4f +/- %.4f",
            name,
            cv_records[-1]["CV R2 (mean)"],
            cv_records[-1]["CV R2 (std)"],
        )

    cv_df = pd.DataFrame(cv_records).set_index("Model")
    return trained_models, cv_df


def get_best_model_name(cv_df: pd.DataFrame) -> str:
    """Return the model name with the highest mean CV R2 score."""
    return cv_df["CV R2 (mean)"].idxmax()
