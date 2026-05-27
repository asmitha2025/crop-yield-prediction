"""
data_loader.py
==============
Handles data loading, validation, and cleaning for the Crop Yield Prediction project.
"""

import logging
import pandas as pd
import numpy as np
from typing import Tuple

logger = logging.getLogger(__name__)

# Column name constants (preserving original dataset typos)
TEMP_COL   = "Temperatue"
YIELD_COL  = "Yeild (Q/acre)"

FEATURE_COLS = [
    "Nitrogen (N)",
    "Phosphorus (P)",
    "Potassium (K)",
    TEMP_COL,
    "Humidity (%)",
    "pH Value",
    "Rain Fall (mm)",
    "Fertilizer",
]

FEATURE_RANGES = {
    "Nitrogen (N)":   (10,  140),
    "Phosphorus (P)": (5,   145),
    "Potassium (K)":  (5,   205),
    TEMP_COL:         (8,    45),
    "Humidity (%)":   (14,  100),
    "pH Value":       (3.5,  9.5),
    "Rain Fall (mm)": (20,  300),
    "Fertilizer":     (10,  300),
}

FEATURE_UNITS = {
    "Nitrogen (N)":   "kg/ha",
    "Phosphorus (P)": "kg/ha",
    "Potassium (K)":  "kg/ha",
    TEMP_COL:         "deg C",
    "Humidity (%)":   "%",
    "pH Value":       "pH",
    "Rain Fall (mm)": "mm",
    "Fertilizer":     "kg/ha",
}


def load_data(filepath: str) -> pd.DataFrame:
    """Load and clean the crop yield Excel dataset.

    Args:
        filepath: Path to the .xlsx file.

    Returns:
        Cleaned DataFrame with all numeric features.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    df = pd.read_excel(filepath)
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

    # Remove invalid temperature entries
    initial = len(df)
    df = df[df[TEMP_COL] != ":"]
    df[TEMP_COL] = pd.to_numeric(df[TEMP_COL], errors="coerce")
    df = df.dropna(subset=[TEMP_COL])
    logger.info("Removed %d invalid temperature rows", initial - len(df))

    # Median-impute remaining nulls in numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            logger.info("Imputed %d nulls in '%s' with median=%.2f", null_count, col, median_val)

    logger.info("Final dataset shape: %s", df.shape)
    return df


def get_features_target(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """Split DataFrame into feature matrix X and target vector y.

    Args:
        df: Cleaned DataFrame.

    Returns:
        Tuple of (X, y).
    """
    X = df[FEATURE_COLS].copy()
    y = df[YIELD_COL].copy()
    return X, y


def get_summary_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Return rounded descriptive statistics."""
    return df[FEATURE_COLS + [YIELD_COL]].describe().round(2)
