import csv
import sqlite3
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
DATABASE_PATH = PROJECT_DIR / "oneDay.db"


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def main() -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        for csv_path in sorted(DATA_DIR.glob("*.csv")):
            table_name = csv_path.stem
            with csv_path.open(encoding="utf-8-sig", newline="") as csv_file:
                reader = csv.DictReader(csv_file)
                columns = reader.fieldnames
                if not columns:
                    continue

                quoted_columns = ", ".join(quote_identifier(column) for column in columns)
                placeholders = ", ".join("?" for _ in columns)
                quoted_table = quote_identifier(table_name)

                connection.execute(f"DROP TABLE IF EXISTS {quoted_table}")
                connection.execute(
                    f"CREATE TABLE {quoted_table} ({quoted_columns})"
                )
                rows = ([row[column] for column in columns] for row in reader)
                connection.executemany(
                    f"INSERT INTO {quoted_table} ({quoted_columns}) VALUES ({placeholders})",
                    rows,
                )
                row_count = connection.execute(
                    f"SELECT COUNT(*) FROM {quoted_table}"
                ).fetchone()[0]
                print(f"{table_name}: {row_count} rows")

    print(f"Database created: {DATABASE_PATH}")


if __name__ == "__main__":
    main()