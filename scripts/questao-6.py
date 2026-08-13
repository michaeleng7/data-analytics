import os
import pandas as pd
import numpy as np
from pathlib import Path

# Directory containing CSV datasets
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_DIR = BASE_DIR / "1-lh_nautical_csv"

# 1. Load datasets
products = pd.read_csv(CSV_DIR / "products.csv")
product_variants = pd.read_csv(CSV_DIR / "product_variants.csv")
orders = pd.read_csv(CSV_DIR / "orders.csv")
order_items = pd.read_csv(CSV_DIR / "order_items.csv")

# Step 1: Filter product "Bússola de Bordo 702" and prepare unified dataset
target_product = products[products["name"] == "Bússola de Bordo 702"]

if target_product.empty:
    print("Product 'Bússola de Bordo 702' not found.")
    exit()

product_id = target_product.iloc[0]["id"]
variant_ids = product_variants[product_variants["product_id"] == product_id]["id"].tolist()

# Filter valid non-cancelled orders
valid_orders = orders[orders["status"].isin(["paid", "confirmed"])].copy()
valid_orders["placed_at"] = pd.to_datetime(valid_orders["placed_at"])

# Merge orders with order items
merged = order_items[order_items["product_variant_id"].isin(variant_ids)].merge(
    valid_orders, left_on="order_id", right_on="id"
)

# Aggregate sales into monthly frequency
merged["year_month"] = merged["placed_at"].dt.to_period("M")
monthly_sales = merged.groupby("year_month")["quantity"].sum().reset_index()

# Build full monthly sequence to handle zero-sales months
min_date = monthly_sales["year_month"].min()
max_date = pd.Period("2026-03", freq="M")
full_periods = pd.period_range(start=min_date, end=max_date, freq="M")

df_full = pd.DataFrame({"year_month": full_periods})
df_full = df_full.merge(monthly_sales, on="year_month", how="left").fillna(0)
df_full["quantity"] = df_full["quantity"].astype(int)

# Step 2: Calculate 3-Month Moving Average (Baseline) using past values
df_full["moving_avg_3m"] = df_full["quantity"].shift(1).rolling(window=3).mean()

# Step 3: Split train (<= 2025-12) and test (2026-01 to 2026-03)
test_periods = [pd.Period("2026-01", freq="M"), pd.Period("2026-02", freq="M"), pd.Period("2026-03", freq="M")]
test_df = df_full[df_full["year_month"].isin(test_periods)].copy()

# Step 4: Calculate MAE
test_df["absolute_error"] = np.abs(test_df["quantity"] - test_df["moving_avg_3m"])
mae = test_df["absolute_error"].mean()

print("--- DEMAND FORECAST RESULTS: Bússola de Bordo 702 ---")
for _, row in test_df.iterrows():
    print(f"Period: {row['year_month']} | Real Sales: {row['quantity']} | Predicted (3M MA): {row['moving_avg_3m']:.2f}")

print(f"\nMean Absolute Error (MAE): {mae:.2f}\n")