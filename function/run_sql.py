import csv
import sqlite3
from pathlib import Path
import re

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
SQL_DIR = PROJECT_DIR / "sql"
DATABASE_PATH = PROJECT_DIR / "oneDay.db"


def quote_identifier(identifier: str) -> str:
    """테이블명과 컬럼명을 SQL에서 안전하게 사용한다."""
    return '"' + identifier.replace('"', '""') + '"'


def load_csv_files(connection: sqlite3.Connection) -> None:
    """data 폴더의 CSV 파일을 같은 이름의 SQLite 테이블로 만든다."""
    for csv_path in sorted(DATA_DIR.glob("*.csv")):
        table_name = csv_path.stem
        quoted_table = quote_identifier(table_name)

        with csv_path.open(encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            columns = reader.fieldnames

            if not columns:
                print(f"{csv_path.name}: 컬럼이 없어 건너뜀")
                continue

            # amount는 숫자로 저장해야 150000 이상 비교가 정확하다.
            column_definitions = ", ".join(
                f'{quote_identifier(column)} '
                f'{"INTEGER" if column == "amount" else "TEXT"}'
                for column in columns
            )
            quoted_columns = ", ".join(
                quote_identifier(column) for column in columns
            )
            placeholders = ", ".join("?" for _ in columns)

            connection.execute(f"DROP TABLE IF EXISTS {quoted_table}")
            connection.execute(
                f"CREATE TABLE {quoted_table} ({column_definitions})"
            )

            rows = (
                [row[column] for column in columns]
                for row in reader
            )
            connection.executemany(
                f"""
                INSERT INTO {quoted_table} ({quoted_columns})
                VALUES ({placeholders})
                """,
                rows,
            )

        row_count = connection.execute(
            f"SELECT COUNT(*) FROM {quoted_table}"
        ).fetchone()[0]
        print(f"{table_name}: {row_count} rows")


def result_title(query: str, fallback: str) -> str:
    """SQL 맨 앞 주석을 결과 파일 제목으로 사용한다."""
    first_line = query.lstrip().splitlines()[0].strip()

    if first_line.startswith("--"):
        title = first_line[2:].strip()
    else:
        title = fallback

    # Windows에서 파일명에 쓸 수 없는 문자 제거
    title = re.sub(r'[<>:"/\\|?*]', "_", title)
    return title.rstrip(" .") or fallback


def run_queries(connection: sqlite3.Connection) -> None:
    """SQL을 실행하고 첫 줄 주석을 제목으로 결과를 출력한다."""
    for question in ("q1", "q2", "q3"):
        sql_files = sorted(SQL_DIR.glob(f"{question}_*.sql"))

        if not sql_files:
            print(f"\n{question}_*.sql: 파일이 없어 건너뜀")
            continue

        for sql_path in sql_files:
            query = sql_path.read_text(encoding="utf-8-sig").strip()

            first_line = query.splitlines()[0].strip()
            title = (
                first_line[2:].strip()
                if first_line.startswith("--")
                else sql_path.stem
            )

            cursor = connection.execute(query)
            columns = [item[0] for item in cursor.description]
            rows = cursor.fetchall()

            print(f"\n[{title}] 결과: {len(rows)}행")
            print(" | ".join(columns))

            for row in rows:
                print(" | ".join(str(value) for value in row))


def main() -> None:
    if not DATA_DIR.exists():
        print(f"data 폴더를 찾을 수 없습니다: {DATA_DIR}")
        return

    with sqlite3.connect(DATABASE_PATH) as connection:
        load_csv_files(connection)
        run_queries(connection)

    print(f"\nDatabase created: {DATABASE_PATH}")


if __name__ == "__main__":
    main()