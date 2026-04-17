import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import create_engine, engine_from_config, pool
from sqlmodel import SQLModel

_lab_root = Path(__file__).resolve().parents[1]
if str(_lab_root) not in sys.path:
    sys.path.insert(0, str(_lab_root))

import app.models  # noqa: F401 - register metadata

from app.core.config import DB_URL  # noqa: E402

config = context.config
config.set_main_option("sqlalchemy.url", DB_URL)

if config.config_file_name is not None:
    try:
        if sys.version_info >= (3, 10):
            fileConfig(config.config_file_name, encoding="utf-8")
        else:
            fileConfig(config.config_file_name)
    except UnicodeDecodeError:
        if sys.version_info >= (3, 10):
            fileConfig(config.config_file_name, encoding="latin-1")

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = config.get_main_option("sqlalchemy.url")
    connectable = create_engine(url)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
