import pandas as pd

# Load the cleaned dataset
df = pd.read_csv("combined_laptop_prices.csv")

# Calculate mean screen size
mean_screen_size = df["screen_size"].mean()

# Fill missing screen size values with the mean
df["screen_size"] = df["screen_size"].fillna(mean_screen_size)

# Verify
print("Missing screen_size values:", df["screen_size"].isna().sum())
print("Mean screen size used:", mean_screen_size)

# Save the updated dataset
df.to_csv("combined_laptop_prices_cleaned.csv", index=False)