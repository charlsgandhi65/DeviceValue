import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the cleaned dataset
df = pd.read_csv("combined_laptop_prices_cleaned.csv")

# -----------------------------
# 1. Price Distribution
# -----------------------------
plt.figure(figsize=(10, 6))
sns.histplot(df["price"], bins=50, kde=True)
plt.title("Laptop Price Distribution")
plt.xlabel("Price (€)")
plt.ylabel("Number of Laptops")
plt.show()


# -----------------------------
# 2. Price vs RAM
# -----------------------------
plt.figure(figsize=(10, 6))
sns.boxplot(x="ram", y="price", data=df)
plt.title("Laptop Price vs RAM")
plt.xlabel("RAM (GB)")
plt.ylabel("Price (€)")
plt.xticks(rotation=45)
plt.show()


# -----------------------------
# 3. Price vs Screen Size
# -----------------------------
plt.figure(figsize=(10, 6))
sns.scatterplot(x="screen_size", y="price", data=df, alpha=0.5)
plt.title("Laptop Price vs Screen Size")
plt.xlabel("Screen Size (inches)")
plt.ylabel("Price (€)")
plt.show()


# -----------------------------
# 4. Price by Brand
# -----------------------------
brand_order = (
    df.groupby("brand")["price"]
    .median()
    .sort_values(ascending=False)
    .index
)

plt.figure(figsize=(14, 7))
sns.boxplot(
    x="brand",
    y="price",
    data=df,
    order=brand_order
)
plt.title("Laptop Price Distribution by Brand")
plt.xlabel("Brand")
plt.ylabel("Price (€)")
plt.xticks(rotation=90)
plt.show()


# -----------------------------
# 5. Price by GPU
# -----------------------------
top_gpus = df["gpu"].value_counts().head(15).index

gpu_df = df[df["gpu"].isin(top_gpus)]

plt.figure(figsize=(14, 7))
sns.boxplot(
    x="gpu",
    y="price",
    data=gpu_df
)
plt.title("Laptop Price by GPU (Top 15 GPUs)")
plt.xlabel("GPU")
plt.ylabel("Price (€)")
plt.xticks(rotation=90)
plt.show()


# -----------------------------
# 6. Price by CPU
# -----------------------------
top_cpus = df["cpu"].value_counts().head(15).index

cpu_df = df[df["cpu"].isin(top_cpus)]

plt.figure(figsize=(14, 7))
sns.boxplot(
    x="cpu",
    y="price",
    data=cpu_df
)
plt.title("Laptop Price by CPU (Top 15 CPUs)")
plt.xlabel("CPU")
plt.ylabel("Price (€)")
plt.xticks(rotation=90)
plt.show()