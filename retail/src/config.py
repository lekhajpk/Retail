import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if load_dotenv:
    load_dotenv(PROJECT_ROOT / ".env")


def get_database_config() -> dict:
    """Return PostgreSQL settings without embedding credentials in source code."""
    return {
        "host": os.getenv("PGHOST", "localhost"),
        "port": int(os.getenv("PGPORT", "5432")),
        "dbname": os.getenv("PGDATABASE", "mobile_banking_dw"),
        "user": os.getenv("PGUSER", "postgres"),
        "password": os.getenv("PGPASSWORD", ""),
    }
