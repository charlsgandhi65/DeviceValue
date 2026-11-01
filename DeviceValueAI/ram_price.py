import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the cleaned dataset
df = pd.read_csv("combined_laptop_prices_cleaned.csv")

# RAM vs Price
plt.figure(figsize=(10, 6))

sns.boxplot(
    x="ram",
    y="price",
    data=df
)

plt.title("Laptop Price vs RAM")
plt.xlabel("RAM (GB)")
plt.ylabel("Price (€)")
plt.xticks(rotation=45)
plt.show()