import os
from pathlib import Path

from dotenv import dotenv_values, load_dotenv

_lab_root = Path(__file__).resolve().parents[2]
_env_path = _lab_root / ".env"


def _default_sqlite_url() -> str:
    path = (_lab_root / "pr3.db").resolve()
    return f"postgresql+psycopg://postgres:mysecretpassword@127.0.0.1:5433/itmo_db"


# JWT and other keys from .env / environment (override OS for local dev)
load_dotenv(_env_path, override=True)

# DB_URL: only if explicitly set in the project .env file (ignore OS-wide DB_URL)
_env_file = dotenv_values(_env_path)
_db_from_file = (_env_file.get("DB_URL") or "").strip()
DB_URL = _db_from_file if _db_from_file else _default_sqlite_url()

JWT_SECRET = os.getenv("JWT_SECRET", "jwt_secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
