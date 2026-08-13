import csv
import os
import re
from datetime import datetime

# Directory where LH Nautical CSV files are located
CSV_DIR = "1-lh_nautical_csv"
OUTPUT_FILE = "schema.sql"

# Standard date/time formats for validation
TIMESTAMP_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M:%S.%f",
]
DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y"]


def is_integer(val: str) -> bool:
    try:
        int(val)
        return True
    except ValueError:
        return False


def is_float(val: str) -> bool:
    try:
        float(val)
        return True
    except ValueError:
        return False


def is_timestamp(val: str) -> bool:
    for fmt in TIMESTAMP_FORMATS:
        try:
            datetime.strptime(val, fmt)
            return True
        except ValueError:
            pass
    return False


def is_date(val: str) -> bool:
    for fmt in DATE_FORMATS:
        try:
            datetime.strptime(val, fmt)
            return True
        except ValueError:
            pass
    return False


def infer_pg_type(values: list) -> str:
    """Infer PostgreSQL-compatible data type based on non-empty values."""
    non_empty = [v.strip() for v in values if v is not None and v.strip() != ""]

    if not non_empty:
        return "VARCHAR(255)"

    # Check for integer types with PostgreSQL limits validation
    if all(is_integer(v) for v in non_empty):
        max_val = max(abs(int(v)) for v in non_empty)
        # PostgreSQL INTEGER max: 2,147,483,647
        if max_val <= 2147483647:
            return "INTEGER"
        # PostgreSQL BIGINT max: 9,223,372,036,854,775,807 (19 digits)
        elif max_val <= 9223372036854775807:
            return "BIGINT"
        # Longer numeric identifiers (e.g., NFe 44-digit keys) fall back to VARCHAR
        else:
            max_len = max(len(v) for v in non_empty)
            return f"VARCHAR({max(max_len * 2, 50)})"

    if all(is_float(v) or is_integer(v) for v in non_empty):
        return "NUMERIC(15, 2)"

    if all(is_timestamp(v) for v in non_empty):
        return "TIMESTAMP"

    if all(is_date(v) for v in non_empty):
        return "DATE"

    # Default string text handling
    max_len = max(len(v) for v in non_empty)
    if max_len > 255:
        return "TEXT"
    return f"VARCHAR({max(max_len * 2, 50)})"


def sanitize_name(name: str) -> str:
    """Sanitize table/column names following PostgreSQL conventions."""
    clean = re.sub(r"[^a-zA-Z0-9_]", "_", name.strip().lower())
    if clean and clean[0].isdigit():
        clean = f"col_{clean}"
    return clean


def generate_schema(csv_folder: str, output_sql: str):
    if not os.path.exists(csv_folder):
        print(f"Error: Directory '{csv_folder}' not found.")
        return

    csv_files = [f for f in os.listdir(csv_folder) if f.endswith(".csv")]

    if not csv_files:
        print(f"No CSV files found in '{csv_folder}'.")
        return

    statements = [
        "-- Automatically generated DDL Schema via Python (Standard Library)\n"
    ]

    for csv_file in sorted(csv_files):
        table_name = sanitize_name(os.path.splitext(csv_file)[0])
        file_path = os.path.join(csv_folder, csv_file)

        with open(file_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            try:
                headers = next(reader)
            except StopIteration:
                continue  # Empty CSV file

            columns_data = {h: [] for h in headers}

            # Read sample rows for performant type inference
            for i, row in enumerate(reader):
                if i >= 1000:
                    break
                for h, val in zip(headers, row):
                    columns_data[h].append(val)

        col_definitions = []
        for col_name in headers:
            sanitized_col = sanitize_name(col_name)
            col_type = infer_pg_type(columns_data[col_name])
            col_definitions.append(f"    {sanitized_col} {col_type}")

        create_table_sql = f"DROP TABLE IF EXISTS {table_name} CASCADE;\n"
        create_table_sql += f"CREATE TABLE {table_name} (\n"
        create_table_sql += ",\n".join(col_definitions)
        create_table_sql += "\n);\n"

        statements.append(create_table_sql)

    with open(output_sql, mode="w", encoding="utf-8") as f:
        f.write("\n".join(statements))

    print(f"Success! File '{output_sql}' generated with {len(csv_files)} tables.")


if __name__ == "__main__":
    generate_schema(CSV_DIR, OUTPUT_FILE)