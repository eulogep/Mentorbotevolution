import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import Flask app models to get metadata
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.models.user import db  # noqa: E402

target_metadata = db.metadata

# Override URL from environment if provided
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    config.set_main_option('sqlalchemy.url', DATABASE_URL)
else:
    # fallback to local sqlite used by app
    default_sqlite = os.path.join(os.path.dirname(__file__), '..', 'database', 'app.db')
    config.set_main_option('sqlalchemy.url', f'sqlite:///{os.path.abspath(default_sqlite)}')


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
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
