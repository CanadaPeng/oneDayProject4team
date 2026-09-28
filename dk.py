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

# print(df.shape)
# df.info()
# df["amount"].describe()
# print(df["amount"].describe())

# Q1

# summary = df.groupby("category")["amount"].agg(total="sum", count="count")
# summary["ratio"] = (summary["total"] / summary["total"].sum() * 100).round(1)
# summary = summary.sort_values("total", ascending=False)
# print(summary)

# plt.rcParams["font.family"] = "Malgun Gothic"
# plt.rcParams["axes.unicode_minus"] = False

# plt.figure(figsize=(10, 6))
# plt.bar(summary.index, summary["ratio"])
# plt.title("카테고리별 지출 비중(%)")
# plt.xlabel("카테고리")
# plt.ylabel("비중(%)")
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.savefig("category_ratio.png")
# plt.show()

# Q2    

THRESHOLD = 150000

big = df[df["amount"] > THRESHOLD]
print(len(big))
print(big["amount"].sum())
print(big.sort_values("amount", ascending=False).head(10))

top10 = big.sort_values("amount", ascending=False).head(10)
print(top10[["date", "category", "amount", "channel"]])

# (a) 카테고리별
big_cat = big.groupby("category")["amount"].agg(total="sum", count="count")
big_cat["ratio"] = (big_cat["total"] / big_cat["total"].sum() * 100).round(1)
big_cat = big_cat.sort_values("total", ascending=False)
print(big_cat)

# (b) 월별
big["month"] = big["date"].str[:7]
big_month = big.groupby("month")["amount"].agg(total="sum", count="count")
print(big_month)

# (c) 채널별
print(big["channel"].value_counts())

summary.to_csv("pandas_q1_category.csv", encoding="utf-8-sig")
big_cat.to_csv("pandas_q2_big_category.csv", encoding="utf-8-sig")
big_month.to_csv("pandas_q2_big_month.csv", encoding="utf-8-sig")