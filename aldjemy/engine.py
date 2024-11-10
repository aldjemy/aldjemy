from typing import TypedDict
import sqlalchemy
from sqlalchemy.engine import URL, make_url
from django.db import connections


_DjangoDBConfig = TypedDict('DjangoDBConfig', {'driver': str})


def _get_driver(engine: str) -> str:
    """Determine the SQLAlchemy driver name from a Django database config."""
    # from django.db.backends.postgresql.psycopg_any import is_psycopg3
    driver = {
        "django.db.backends.sqlite3": "sqlite",
        "django.db.backends.mysql": "mysql",
        "django.db.backends.postgresql": "postgresql",
        "django.db.backends.postgresql_psycopg2": "postgresql",
        "django.db.backends.oracle": "oracle",
    }.get(engine)
    if not driver:
        raise ValueError(f"Unsupported database engine {engine!r}")
    return driver


def _get_engine_url(config: _DjangoDBConfig) -> URL:
    driver = _get_driver(config["ENGINE"])
    name = config.get("NAME") or ""
    if driver.startswith("sqlite") and name.startswith("file:"):
        # It's a SQLite URL, let the SQLAlchemy driver know that.
        name = f"{name}&uri=true"

    url = URL.create(
        drivername=driver,
        username=config.get("USER") or None,
        password=config.get("PASSWORD") or None,
        host=config.get("HOST") or None,
        port=config.get("PORT") or None,
        database=name or None,
    )

    # Encode as a string and convert back to a URL object in order to
    # handle database names that contain query strings, such as
    # SQLite's "file:filename?cache=shared".
    return make_url(str(url))


def create_engine(alias: str = "default"):
    """Create a SQLAlchemy engine from a Django database alias."""
    # The settings_dict attribute reflects testing overrides,
    # where directly reading the DATABASES setting does not.
    config = connections[alias].settings_dict
    url = _get_engine_url(config)
    return sqlalchemy.create_engine(url)
