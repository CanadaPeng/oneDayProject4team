"""
brief_seongho.py  (6번 AI 활용 + 브리핑 담당: 이성호)

역할: 거래 데이터에서 '매일 확인할 핵심 지표 5개'를 뽑아
      1) output/briefing.md   : 사람이 읽는 브리핑 (result_report.md에 붙여 넣기용)
      2) output/brief.json    : n8n이 가져가서 메일로 보내는 데이터
      를 만든다.

실행: python brief_seongho.py
"""
import json
from pathlib import Path

import pandas as pd

# ── 설정 ─────────────────────────────────────────────
DATA_DIR = Path("data")
OUT_DIR = Path("output")
TOP_N = 3  # 카테고리 TOP N
# Q2 '큰 금액' 기준: 팀 합의값 150,000원 (2번 SQL·3번 Pandas A와 동일해야 함)
# 기준이 바뀌면 이 숫자 하나만 고친다.
HIGH_AMOUNT_THRESHOLD = 150_000

WEEKDAY_KO = ["월", "화", "수", "목", "금", "토", "일"]


def time_band(hour: int) -> str:
    """시(hour)를 시간대 이름으로 바꾼다."""
    if hour < 6:
        return "새벽(00~06시)"
    if hour < 12:
        return "오전(06~12시)"
    if hour < 18:
        return "오후(12~18시)"
    return "저녁(18~24시)"


def won(x: float) -> str:
    """숫자를 '1,234,567원' 형식으로."""
    return f"{int(round(x)):,}원"


# ── 1. 데이터 불러오기 ─────────────────────────────────
tx = pd.read_csv(DATA_DIR / "transactions.csv", encoding="utf-8-sig")
cat = pd.read_csv(DATA_DIR / "categories.csv", encoding="utf-8-sig")
tx = tx.merge(cat[["category", "category_name"]], on="category", how="left")

tx["date"] = pd.to_datetime(tx["date"])
tx["month"] = tx["date"].dt.strftime("%Y-%m")
tx["weekday"] = tx["date"].dt.dayofweek.map(lambda i: WEEKDAY_KO[i])
tx["hour"] = tx["time"].str.slice(0, 2).astype(int)
tx["time_band"] = tx["hour"].map(time_band)

total = tx["amount"].sum()
n = len(tx)

# ── 2. 지표 ①: 전체 규모 ───────────────────────────────
period = f"{tx['date'].min():%Y-%m-%d} ~ {tx['date'].max():%Y-%m-%d}"

# ── 3. 지표 ②: 카테고리 TOP N (Q1) ─────────────────────
by_cat = (
    tx.groupby("category_name")["amount"]
    .agg(금액="sum", 건수="count")
    .sort_values("금액", ascending=False)
)
by_cat["비중(%)"] = (by_cat["금액"] / total * 100).round(1)
top_cat = by_cat.head(TOP_N)

# ── 4. 지표 ③: 큰 금액 거래 (Q2) ───────────────────────
threshold = HIGH_AMOUNT_THRESHOLD
rule_text = f"{won(threshold)} 이상 (팀 합의 기준)"
high = tx[tx["amount"] >= threshold]
high_share = high["amount"].sum() / total * 100
high_top_cat = high["category_name"].value_counts().idxmax()

# ── 5. 지표 ④·⑤: 기간 패턴 (Q3) ────────────────────────
by_month = tx.groupby("month")["amount"].sum()
peak_month, low_month = by_month.idxmax(), by_month.idxmin()
by_weekday = tx.groupby("weekday")["amount"].sum()
peak_weekday = by_weekday.idxmax()
by_band = tx.groupby("time_band")["amount"].sum()
peak_band = by_band.idxmax()

# ── 6. 브리핑 문장 만들기 ──────────────────────────────
kpis = [
    {"지표": "전체 지출", "값": f"{won(total)} ({n:,}건, 건당 평균 {won(total / n)})"},
    {
        "지표": f"지출 1위 카테고리",
        "값": f"{top_cat.index[0]} {won(top_cat['금액'].iloc[0])} (비중 {top_cat['비중(%)'].iloc[0]}%)",
    },
    {
        "지표": "큰 금액 거래",
        "값": f"{len(high)}건({len(high) / n * 100:.1f}%)이 전체 지출의 {high_share:.1f}% 차지 · 기준 {won(threshold)} 이상 · 최다 {high_top_cat}",
    },
    {
        "지표": "월별 최고/최저",
        "값": f"최고 {peak_month} {won(by_month.max())} / 최저 {low_month} {won(by_month.min())}",
    },
    {"지표": "지출 집중 시점", "값": f"{peak_weekday}요일 · {peak_band}"},
]

lines = [
    "# 소비패턴 데일리 브리핑",
    "",
    f"- 분석 기간: {period}",
    f"- 데이터: 가상 거래 {n:,}건 (실제 소비 실태가 아닌 분석 방법 검증용)",
    f"- 큰 금액 기준: {rule_text}",
    "",
    "## 핵심 지표 5",
    "",
    "| 지표 | 값 |",
    "|---|---|",
]
lines += [f"| {k['지표']} | {k['값']} |" for k in kpis]
lines += ["", f"## 카테고리 TOP {TOP_N}", "", "| 순위 | 카테고리 | 금액 | 건수 | 비중 |", "|---|---|---|---|---|"]
for i, (name, row) in enumerate(top_cat.iterrows(), start=1):
    lines.append(f"| {i} | {name} | {won(row['금액'])} | {int(row['건수'])} | {row['비중(%)']}% |")

briefing_md = "\n".join(lines) + "\n"

# 메일 본문(텍스트)
body = "\n".join(
    [f"[소비패턴 데일리 브리핑] {period}", ""]
    + [f"{i}. {k['지표']}: {k['값']}" for i, k in enumerate(kpis, start=1)]
    + ["", "※ 가상 데이터 기반 분석 결과이며, 수치는 SQL·Pandas 교차검증(5번)을 거쳤습니다."]
)

# ── 7. 저장 ───────────────────────────────────────────
OUT_DIR.mkdir(exist_ok=True)
(OUT_DIR / "briefing.md").write_text(briefing_md, encoding="utf-8")
(OUT_DIR / "brief.json").write_text(
    json.dumps(
        {
            "subject": f"[소비패턴 브리핑] 지출 1위 {top_cat.index[0]} · 큰 금액 거래 {len(high)}건",
            "body": body,
            "kpis": kpis,
        },
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)

print(briefing_md)
print("저장 완료: output/briefing.md, output/brief.json")