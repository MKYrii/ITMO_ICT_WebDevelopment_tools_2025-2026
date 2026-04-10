# -*- coding: utf-8 -*-
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
from app.models import *
from sqlmodel import SQLModel

# Ensure imports like "app.*" work no matter where alembic is launched from
_lab_root = Path(__file__).resolve().parents[1]
if str(_lab_root) not in sys.path:
    sys.path.insert(0, str(_lab_root))

load_dotenv(_lab_root / ".env")

config = context.config

_ini_url = config.get_main_option("sqlalchemy.url")
if _ini_url:
    config.set_main_option("sqlalchemy.url", os.getenv("DB_URL", _ini_url))

if config.config_file_name is not None:
    try:
        if sys.version_info >= (3, 10):
            fileConfig(config.config_file_name, encoding="utf-8")
        else:
            fileConfig(config.config_file_name)
    except UnicodeDecodeError:
        if sys.version_info >= (3, 10):
            fileConfig(config.config_file_name, encoding="latin-1")
        # Py < 3.10: skip broken logging section rather than failing migrations

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
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
