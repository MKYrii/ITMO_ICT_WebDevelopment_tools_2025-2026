"""Create SQLite file and tables via SQLModel (same schema as models)."""
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import app.models  # noqa: F401, E402 - register tables on metadata
from app.core.config import DB_URL  # noqa: E402
from app.db import init_db  # noqa: E402


def main() -> None:
    init_db()
    print(f"OK: tables created (if missing). DB_URL={DB_URL}")


if __name__ == "__main__":
    main()
