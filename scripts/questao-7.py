import os
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path

# Directory containing CSV datasets (resolved relative to this script)
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_DIR = BASE_DIR / "1-lh_nautical_csv"

# 1. Load datasets
products = pd.read_csv(CSV_DIR / "products.csv")
product_variants = pd.read_csv(CSV_DIR / "product_variants.csv")
orders = pd.read_csv(CSV_DIR / "orders.csv")
order_items = pd.read_csv(CSV_DIR / "order_items.csv")

# Identify target reference product: "Motor de Popa 1949"
target_name = "Motor de Popa 1949"
target_product = products[products["name"] == target_name]

if target_product.empty:
    print(f"Product '{target_name}' not found.")
    exit()

target_product_id = target_product.iloc[0]["id"]

# 2. Map transaction chain for valid sales (paid/confirmed)
valid_orders = orders[orders["status"].isin(["paid", "confirmed"])]

# Join order_items -> product_variants -> products
items_variants = order_items.merge(
    product_variants[["id", "product_id"]],
    left_on="product_variant_id",
    right_on="id"
)

df_merged = items_variants.merge(
    valid_orders[["id", "customer_id"]],
    left_on="order_id",
    right_on="id"
)

# 3. Build User x Product Interaction Matrix (Presence/Absence)
# Rows: customer_id | Columns: product_id | Value: 1 if purchased, 0 otherwise
user_product_matrix = df_merged.pivot_table(
    index="customer_id",
    columns="product_id",
    values="quantity",
    aggfunc=lambda x: 1 if len(x) > 0 else 0,
    fill_value=0
)

# Transpose matrix to obtain Product x User structure for product-based similarity
product_user_matrix = user_product_matrix.T

# 4. Compute Cosine Similarity between products
cosine_sim_matrix = cosine_similarity(product_user_matrix)

# Create DataFrame for similarity scores
products_list = product_user_matrix.index.tolist()
sim_df = pd.DataFrame(cosine_sim_matrix, index=products_list, columns=products_list)

# 5. Extract top recommendations for "Motor de Popa 1949" (excluding itself)
target_similarities = sim_df[target_product_id].drop(index=target_product_id)

recommendations = target_similarities.reset_index()
recommendations.columns = ["product_id", "similarity_score"]

recommendations = recommendations.merge(products[["id", "name"]], left_on="product_id", right_on="id")
top_5_recommendations = recommendations.sort_values(by="similarity_score", ascending=False).head(5)

# Output recommendation results
print(f"--- RECOMMENDATIONS FOR: '{target_name}' ---\n")
for idx, row in top_5_recommendations.reset_index(drop=True).iterrows():
    print(f"{idx+1}. {row['name']} | Similarity Score: {row['similarity_score']:.4f}")
