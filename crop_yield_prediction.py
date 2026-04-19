"""
crop_yield_prediction.py
========================
Command-line pipeline for the Crop Yield Prediction project.
Uses the modularized src components to train and evaluate models.
"""

import logging
import sys
import os
import pickle
import pandas as pd

from src.data_loader import load_data, get_features_target, get_summary_stats
from src.model_trainer import train_all_models, get_best_model_name
from src.evaluator import compute_all_metrics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("CropYieldPipeline")

DATA_FILE = "crop yield data sheet.xlsx"
MODEL_FILE = "crop_yield_model.pkl"


def main():
    logger.info("="*60)
    logger.info("CROP YIELD PREDICTION PIPELINE")
    logger.info("="*60)

    # 1. Load Data
    logger.info("\n[STEP 1] Data Loading & Validation")
    if not os.path.exists(DATA_FILE):
        logger.error("Dataset '%s' not found! Run generate_dataset.py first.", DATA_FILE)
        sys.exit(1)
        
    df = load_data(DATA_FILE)
    logger.info("Summary Statistics:\n%s", get_summary_stats(df).to_string())

    # 2. Split Features & Target
    logger.info("\n[STEP 2] Prepare Data for Modeling")
    X, y = get_features_target(df)
    
    # Simple Train/Test split for final holdout evaluation
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    logger.info("Train shape: %s | Test shape: %s", X_train.shape, X_test.shape)

    # 3. Train Models with Cross Validation
    logger.info("\n[STEP 3] Model Training (5-Fold CV)")
    models, cv_df = train_all_models(X_train, y_train)
    
    logger.info("\nCross-Validation Results:\n%s", cv_df.to_string())

    # 4. Final Evaluation on Holdout Test Set
    logger.info("\n[STEP 4] Holdout Set Evaluation")
    metrics_df = compute_all_metrics(models, X_test, y_test)
    logger.info("\nTest Set Metrics:\n%s", metrics_df.to_string())

    # 5. Save Best Model
    logger.info("\n[STEP 5] Saving Best Model")
    best_name = get_best_model_name(cv_df)
    best_model = models[best_name]
    
    with open(MODEL_FILE, "wb") as f:
        pickle.dump(best_model, f)
        
    logger.info("WINNER: %s (Saved to %s)", best_name, MODEL_FILE)
    
    logger.info("="*60)
    logger.info("PIPELINE COMPLETED SUCCESSFULLY")
    logger.info("="*60)


if __name__ == "__main__":
    main()
