import os
import psycopg
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}

# Directory containing CSV datasets
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_DIR = BASE_DIR / "1-lh_nautical_csv"


def ingest_csv_to_postgres():
    if not os.path.exists(CSV_DIR):
        print(f"Error: Directory '{CSV_DIR}' not found.")
        return

    csv_files = [f for f in os.listdir(CSV_DIR) if f.endswith(".csv")]

    if not csv_files:
        print(f"No CSV files found in '{CSV_DIR}'.")
        return

    try:
        # Psycopg3 handles binary streams natively without forcing UTF-8
        with psycopg.connect(**DB_CONFIG) as conn:
            print("Successfully connected to PostgreSQL!\n")
            with conn.cursor() as cur:
                for csv_file in sorted(csv_files):
                    table_name = os.path.splitext(csv_file)[0].lower().strip()
                    file_path = os.path.abspath(os.path.join(CSV_DIR, csv_file))

                    print(f"Loading raw data from {csv_file} -> Table '{table_name}'...")

                    with open(file_path, "rb") as f:
                        sql_copy = f"""
                            COPY {table_name}
                            FROM STDIN
                            WITH (
                                FORMAT csv,
                                HEADER true,
                                DELIMITER ',',
                                QUOTE '"',
                                ESCAPE '"'
                            );
                        """
                        with cur.copy(sql_copy) as copy:
                            while data := f.read(8192):
                                copy.write(data)

                    conn.commit()
                    print(f"  └─ Success: {csv_file} loaded without modifications.")

        print("\nRaw data ingestion completed for all tables!")

    except Exception as e:
        print(f"\nExecution error: {e}")


if __name__ == "__main__":
    ingest_csv_to_postgres()