"""
Generate a realistic crop yield dataset for the Crop Yield Prediction project.
Creates 'crop yield data sheet.xlsx' with realistic agricultural data.
"""

import pandas as pd
import numpy as np

np.random.seed(42)
n_samples = 1000

# Generate realistic agricultural data
data = {
    'Nitrogen (N)': np.random.uniform(10, 140, n_samples).round(2),
    'Phosphorus (P)': np.random.uniform(5, 145, n_samples).round(2),
    'Potassium (K)': np.random.uniform(5, 205, n_samples).round(2),
    'Temperatue': np.random.uniform(8, 45, n_samples).round(2),  # Keeping original typo
    'Humidity (%)': np.random.uniform(14, 100, n_samples).round(2),
    'pH Value': np.random.uniform(3.5, 9.5, n_samples).round(2),
    'Rain Fall (mm)': np.random.uniform(20, 300, n_samples).round(2),
    'Fertilizer': np.random.uniform(10, 300, n_samples).round(2),
}

df = pd.DataFrame(data)

# Generate yield based on a realistic non-linear relationship
yield_values = (
    0.15 * df['Nitrogen (N)']
    + 0.10 * df['Phosphorus (P)']
    + 0.08 * df['Potassium (K)']
    + 0.5 * df['Rain Fall (mm)'] / 10
    - 0.3 * np.abs(df['Temperatue'] - 25)   # optimal temp ~25 deg C
    - 2.0 * np.abs(df['pH Value'] - 6.5)     # optimal pH ~6.5
    + 0.05 * df['Fertilizer']
    + 0.02 * df['Humidity (%)']
    + np.random.normal(0, 2, n_samples)       # noise
)

# Clamp to realistic range
df['Yeild (Q/acre)'] = np.clip(yield_values, 1, 60).round(2)  # Keeping original typo

# Inject a few ':' values in Temperature to simulate the original data issue
bad_indices = np.random.choice(n_samples, size=5, replace=False)
df.loc[bad_indices, 'Temperatue'] = ':'

print(f"Dataset shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
print(f"\nFirst 5 rows:")
print(df.head())
print(f"\nBad temperature rows (index): {bad_indices.tolist()}")

# Save as Excel
df.to_excel("crop yield data sheet.xlsx", index=False)
print("\nDataset saved to 'crop yield data sheet.xlsx'")
