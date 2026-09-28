"""
validation_suyeon.py  (5번 검증 담당: 김수연)

역할:
SQL과 Pandas의 분석 결과를 교차 검증하여
동일한 기준으로 계산된 값이 서로 일치하는지 확인한다.

검증 항목:
1. 전체 행 수
2. 전체 금액
3. 카테고리별 건수
4. 카테고리별 금액
5. 150,000원 이상 고액 거래 건수
6. 월별 지출 합계
7. 요일별 지출 합계

산출물:
    validation_suyeon.py

실행:
    python validation_suyeon.py
"""

from pathlib import Path
import sqlite3
import pandas as pd


# --------------------------------------------------
# 0. 경로 설정
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
SQL_DIR = PROJECT_DIR / "sql"
OUTPUT_DIR = PROJECT_DIR / "output"

HIGH_AMOUNT = 150_000


# --------------------------------------------------
# 1. 데이터 불러오기
# --------------------------------------------------

def load_data():
    """프로젝트의 원본 CSV 4개를 불러온다."""
    transactions = pd.read_csv(DATA_DIR / "transactions.csv")
    categories = pd.read_csv(DATA_DIR / "categories.csv")
    customers = pd.read_csv(DATA_DIR / "customers.csv")
    merchants = pd.read_csv(DATA_DIR / "merchants.csv")

    # 비교를 위해 금액은 숫자형, 날짜는 datetime으로 통일
    transactions["amount"] = pd.to_numeric(transactions["amount"])
    transactions["date"] = pd.to_datetime(transactions["date"])

    return transactions, categories, customers, merchants


# --------------------------------------------------
# 2. SQLite에 동일 원본 데이터 적재
# --------------------------------------------------

def make_database(transactions, categories, customers, merchants):
    """
    SQL 담당자의 쿼리를 그대로 실행할 수 있도록
    동일한 원본 데이터를 SQLite 메모리 DB에 적재한다.
    """
    conn = sqlite3.connect(":memory:")

    # SQL의 strftime이 동작하도록 날짜는 YYYY-MM-DD 문자열로 저장
    sql_transactions = transactions.copy()
    sql_transactions["date"] = sql_transactions["date"].dt.strftime("%Y-%m-%d")

    sql_transactions.to_sql("transactions", conn, index=False, if_exists="replace")
    categories.to_sql("categories", conn, index=False, if_exists="replace")
    customers.to_sql("customers", conn, index=False, if_exists="replace")
    merchants.to_sql("merchants", conn, index=False, if_exists="replace")

    return conn


# --------------------------------------------------
# 3. SQL 파일 실행
# --------------------------------------------------

def run_sql_file(conn, question):
    """
    sql/q1_*.sql, q2_*.sql, q3_*.sql 중
    해당 질문의 SQL 파일을 찾아 실행한 결과를 DataFrame으로 반환한다.
    """
    sql_files = sorted(SQL_DIR.glob(f"{question}_*.sql"))

    if not sql_files:
        raise FileNotFoundError(
            f"{SQL_DIR} 폴더에서 {question}_*.sql 파일을 찾지 못했습니다."
        )

    sql_path = sql_files[0]
    query = sql_path.read_text(encoding="utf-8-sig")

    return pd.read_sql_query(query, conn)


# --------------------------------------------------
# 4. Pandas 기준 결과 계산
# --------------------------------------------------

def make_pandas_results(df):
    """SQL과 같은 기준으로 Pandas 결과를 계산한다."""

    # Q1. 카테고리별 건수 / 금액
    q1 = (
        df.groupby("category", as_index=False)
        .agg(
            transaction_count=("transaction_id", "count"),
            total_amount=("amount", "sum"),
        )
    )

    # Q2. 150,000원 이상 고액 거래
    q2 = df[df["amount"] >= HIGH_AMOUNT].copy()

    # Q3-1. 월별 지출
    monthly = (
        df.assign(month=df["date"].dt.strftime("%m"))
        .groupby("month", as_index=False)
        .agg(
            transaction_count=("transaction_id", "count"),
            total_amount=("amount", "sum"),
        )
    )

    # Q3-2. 요일별 지출
    # SQLite strftime('%w') 기준:
    # 0=일요일, 1=월요일, ..., 6=토요일
    weekday_code = ((df["date"].dt.dayofweek + 1) % 7).astype(str)

    weekday = (
        df.assign(weekday=weekday_code)
        .groupby("weekday", as_index=False)
        .agg(
            transaction_count=("transaction_id", "count"),
            total_amount=("amount", "sum"),
        )
    )

    return q1, q2, monthly, weekday


# --------------------------------------------------
# 5. 비교 함수
# --------------------------------------------------

def compare_frames(left, right, key, value_columns):
    """
    두 DataFrame을 key 기준으로 합친 뒤
    지정한 값들이 전부 일치하는지 확인한다.
    """
    left = left.copy()
    right = right.copy()

    left[key] = left[key].astype(str)
    right[key] = right[key].astype(str)

    merged = left.merge(
        right,
        on=key,
        how="outer",
        suffixes=("_sql", "_pandas"),
        indicator=True,
    )

    same = (merged["_merge"] == "both")

    for col in value_columns:
        same = same & (
            merged[f"{col}_sql"].fillna(-1)
            == merged[f"{col}_pandas"].fillna(-1)
        )

    return bool(same.all()), merged


# --------------------------------------------------
# 6. 검증 실행
# --------------------------------------------------

def main():
    transactions, categories, customers, merchants = load_data()
    conn = make_database(transactions, categories, customers, merchants)

    try:
        # SQL 담당자 결과
        sql_q1 = run_sql_file(conn, "q1")
        sql_q2 = run_sql_file(conn, "q2")
        sql_q3 = run_sql_file(conn, "q3")

        # Pandas 결과
        pd_q1, pd_q2, pd_month, pd_weekday = make_pandas_results(transactions)

        # --------------------------------------------------
        # 6-1. 전체 행 수
        # --------------------------------------------------
        sql_total_rows = pd.read_sql_query(
            "SELECT COUNT(*) AS total_rows FROM transactions", conn
        ).loc[0, "total_rows"]

        pandas_total_rows = len(transactions)
        row_match = sql_total_rows == pandas_total_rows

        # --------------------------------------------------
        # 6-2. 전체 금액
        # --------------------------------------------------
        sql_total_amount = pd.read_sql_query(
            "SELECT SUM(amount) AS total_amount FROM transactions", conn
        ).loc[0, "total_amount"]

        pandas_total_amount = transactions["amount"].sum()
        amount_match = sql_total_amount == pandas_total_amount

        # --------------------------------------------------
        # 6-3 / 6-4. 카테고리별 건수 / 금액
        # --------------------------------------------------
        q1_sql = sql_q1[
            ["category", "transaction_count", "total_amount"]
        ].copy()

        category_count_match, q1_count_detail = compare_frames(
            q1_sql[["category", "transaction_count"]],
            pd_q1[["category", "transaction_count"]],
            key="category",
            value_columns=["transaction_count"],
        )

        category_amount_match, q1_amount_detail = compare_frames(
            q1_sql[["category", "total_amount"]],
            pd_q1[["category", "total_amount"]],
            key="category",
            value_columns=["total_amount"],
        )

        # --------------------------------------------------
        # 6-5. 150,000원 이상 고액 거래 건수
        # --------------------------------------------------
        sql_high_count = len(sql_q2)
        pandas_high_count = len(pd_q2)
        high_count_match = sql_high_count == pandas_high_count

        # 건수뿐 아니라 실제 transaction_id도 동일한지 확인
        sql_high_ids = set(sql_q2["transaction_id"].astype(str))
        pandas_high_ids = set(pd_q2["transaction_id"].astype(str))
        high_id_match = sql_high_ids == pandas_high_ids

        # --------------------------------------------------
        # 6-6. 월별 지출 합계
        # --------------------------------------------------
        sql_month = (
            sql_q3[sql_q3["period_type"] == "month"][
                ["period_value", "transaction_count", "total_amount"]
            ]
            .rename(columns={"period_value": "month"})
            .copy()
        )

        month_match, month_detail = compare_frames(
            sql_month,
            pd_month,
            key="month",
            value_columns=["transaction_count", "total_amount"],
        )

        # --------------------------------------------------
        # 6-7. 요일별 지출 합계
        # --------------------------------------------------
        sql_weekday = (
            sql_q3[sql_q3["period_type"] == "weekday"][
                ["period_value", "transaction_count", "total_amount"]
            ]
            .rename(columns={"period_value": "weekday"})
            .copy()
        )

        weekday_match, weekday_detail = compare_frames(
            sql_weekday,
            pd_weekday,
            key="weekday",
            value_columns=["transaction_count", "total_amount"],
        )

        # --------------------------------------------------
        # 7. 검증 기준표 작성
        # --------------------------------------------------
        validation_table = pd.DataFrame(
            [
                {
                    "검증항목": "전체 행 수",
                    "SQL결과": sql_total_rows,
                    "Pandas결과": pandas_total_rows,
                    "일치여부": "일치" if row_match else "불일치",
                },
                {
                    "검증항목": "전체 금액",
                    "SQL결과": sql_total_amount,
                    "Pandas결과": pandas_total_amount,
                    "일치여부": "일치" if amount_match else "불일치",
                },
                {
                    "검증항목": "카테고리별 건수",
                    "SQL결과": "카테고리별 집계",
                    "Pandas결과": "카테고리별 집계",
                    "일치여부": "일치" if category_count_match else "불일치",
                },
                {
                    "검증항목": "카테고리별 금액",
                    "SQL결과": "카테고리별 집계",
                    "Pandas결과": "카테고리별 집계",
                    "일치여부": "일치" if category_amount_match else "불일치",
                },
                {
                    "검증항목": f"{HIGH_AMOUNT:,}원 이상 고액 거래 건수",
                    "SQL결과": sql_high_count,
                    "Pandas결과": pandas_high_count,
                    "일치여부": (
                        "일치"
                        if high_count_match and high_id_match
                        else "불일치"
                    ),
                },
                {
                    "검증항목": "월별 지출 합계",
                    "SQL결과": "월별 집계",
                    "Pandas결과": "월별 집계",
                    "일치여부": "일치" if month_match else "불일치",
                },
                {
                    "검증항목": "요일별 지출 합계",
                    "SQL결과": "요일별 집계",
                    "Pandas결과": "요일별 집계",
                    "일치여부": "일치" if weekday_match else "불일치",
                },
            ]
        )

        # --------------------------------------------------
        # 8. 결과 출력
        # --------------------------------------------------
        print("\n" + "=" * 65)
        print("SQL vs Pandas 교차 검증 결과")
        print("=" * 65)
        print(validation_table.to_string(index=False))

        all_match = (validation_table["일치여부"] == "일치").all()

        print("\n[최종 결과]")
        if all_match:
            print("모든 검증 항목이 일치합니다.")
        else:
            print("일부 검증 항목이 불일치합니다. 상세 결과를 확인하세요.")

        # 고액거래 transaction_id까지 확인
        if not high_id_match:
            print("\n[고액 거래 불일치]")
            print("SQL에만 있는 ID:", sorted(sql_high_ids - pandas_high_ids))
            print("Pandas에만 있는 ID:", sorted(pandas_high_ids - sql_high_ids))

        # --------------------------------------------------
        # 9. 검증 결과 저장
        # --------------------------------------------------
        OUTPUT_DIR.mkdir(exist_ok=True)
        validation_table.to_csv(
            OUTPUT_DIR / "validation_result.csv",
            index=False,
            encoding="utf-8-sig",
        )

        print("\n검증 결과 저장:")
        print(OUTPUT_DIR / "validation_result.csv")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
