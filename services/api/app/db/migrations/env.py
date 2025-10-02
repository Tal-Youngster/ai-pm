"""Alembic environment configuration."""

from __future__ import annotations

from configparser import NoSectionError
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.config import Settings
from app.db.models import Base

config = context.config

if config.config_file_name is not None:
    try:
        fileConfig(config.config_file_name)
    except (KeyError, NoSectionError):
        pass


def get_url() -> str:
    settings = Settings()
    return settings.database_url


target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    if config is not None:
        config.set_main_option('sqlalchemy.url', url)

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = {}
    if config is not None:
        configuration = config.get_section(config.config_ini_section, {})
    configuration['sqlalchemy.url'] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
