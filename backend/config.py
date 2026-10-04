"""Load local configuration without storing credentials in source code."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


class DatabaseConfigurationError(ValueError):
    """Required database settings are missing or invalid."""


def get_db_config():
    if not os.getenv("DB_USER") or not os.getenv("DB_PASSWORD"):
        raise DatabaseConfigurationError("Set DB_USER and DB_PASSWORD in .env.")
    try:
        port = int(os.getenv("DB_PORT", "3306"))
        if not 1 <= port <= 65535:
            raise ValueError
    except ValueError:
        raise DatabaseConfigurationError("DB_PORT must be a valid port number.") from None

    return {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "port": port,
        "user": os.environ["DB_USER"],
        "password": os.environ["DB_PASSWORD"],
        "database": os.getenv("DB_NAME", "expense_manager"),
        "connection_timeout": 5,
        "autocommit": False,
    }
