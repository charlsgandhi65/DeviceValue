import pandas as pd

# Load the cleaned dataset
df = pd.read_csv("combined_laptop_prices.csv")

# 1. Dataset size
print("Dataset Shape:")
print(df.shape)

# 2. Column names
print("\nColumns:")
print(df.columns.tolist())

# 3. Data types
print("\nData Types:")
print(df.dtypes)

# 4. Missing values
print("\nMissing Values:")
print(df.isnull().sum())

# 5. Duplicate rows
print("\nDuplicate Rows:")
print(df.duplicated().sum())

# 6. Basic statistical summary
print("\nStatistical Summary:")
print(df.describe(include="all"))

# 7. Number of unique values in each column
print("\nUnique Values:")
print(df.nunique())

# 8. Price statistics
print("\nPrice Statistics:")
print("Minimum Price:", df["price"].min())
print("Maximum Price:", df["price"].max())
print("Mean Price:", df["price"].mean())
print("Median Price:", df["price"].median())

# 9. First 10 records
print("\nFirst 10 Records:")
print(df.head(10))