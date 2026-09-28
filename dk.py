import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/categories.csv")
df.head()
df = pd.read_csv("data/customers.csv")
df.head()
df = pd.read_csv("data/merchants.csv")
df.head()
df = pd.read_csv("data/transactions.csv")
df.head()

print(df.shape)
df.info()
df["amount"].describe()
print(df["amount"].describe())

# Q1

summary = df.groupby("category")["amount"].agg(total="sum", count="count")
summary["ratio"] = (summary["total"] / summary["total"].sum() * 100).round(1)
summary = summary.sort_values("total", ascending=False)
print(summary)

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

plt.figure(figsize=(10, 6))
plt.bar(summary.index, summary["ratio"])
plt.title("카테고리별 지출 비중(%)")
plt.xlabel("카테고리")
plt.ylabel("비중(%)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("category_ratio.png")
plt.show()

# Q2    


