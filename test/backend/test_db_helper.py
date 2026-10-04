from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import mysql.connector
import pytest

from backend import db_helper
from backend.config import DatabaseConfigurationError, get_db_config


@pytest.fixture
def database(monkeypatch):
    connection = MagicMock()
    cursor = connection.cursor.return_value
    monkeypatch.setattr(db_helper.mysql.connector, "connect", lambda **kwargs: connection)
    return connection, cursor


def test_replacement_commits_once_and_binds_values(database):
    connection, cursor = database
    note = "Example'); DROP TABLE expenses; --"
    db_helper.replace_expenses_for_date(date(2026, 9, 3), [
        {"amount": Decimal("12.50"), "category": "Food", "notes": note},
    ])
    connection.commit.assert_called_once()
    connection.rollback.assert_not_called()
    query, rows = cursor.executemany.call_args.args
    assert note not in query
    assert rows == [(date(2026, 9, 3), Decimal("12.50"), "Food", note)]
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


def test_insert_failure_rolls_back_replacement(database):
    connection, cursor = database
    cursor.executemany.side_effect = mysql.connector.IntegrityError("Synthetic failure")
    with pytest.raises(mysql.connector.IntegrityError):
        db_helper.replace_expenses_for_date("2026-09-03", [
            {"amount": 12.50, "category": "Food", "notes": "Sample"},
        ])
    connection.commit.assert_not_called()
    connection.rollback.assert_called_once()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


def test_commit_failure_rolls_back_and_closes(database):
    connection, cursor = database
    connection.commit.side_effect = mysql.connector.Error("Synthetic commit failure")
    with pytest.raises(mysql.connector.Error):
        db_helper.replace_expenses_for_date("2026-09-03", [])
    connection.rollback.assert_called_once()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


def test_cursor_creation_failure_closes_connection(database):
    connection, _ = database
    connection.cursor.side_effect = mysql.connector.Error("Synthetic cursor failure")
    with pytest.raises(mysql.connector.Error):
        db_helper.fetch_expenses_for_date("2026-09-03")
    connection.close.assert_called_once()


def test_empty_replacement_clears_only_selected_date(database):
    connection, cursor = database
    db_helper.replace_expenses_for_date("2026-09-03", [])
    cursor.execute.assert_called_once_with(
        "DELETE FROM expenses WHERE expense_date = %s", ("2026-09-03",)
    )
    cursor.executemany.assert_not_called()
    connection.commit.assert_called_once()


def test_empty_fetch_does_not_commit(database):
    connection, cursor = database
    cursor.fetchall.return_value = []
    assert db_helper.fetch_expenses_for_date("2033-01-01") == []
    connection.commit.assert_not_called()


def test_missing_password_fails_before_connecting(monkeypatch):
    monkeypatch.setenv("DB_USER", "test_user")
    monkeypatch.delenv("DB_PASSWORD", raising=False)
    with pytest.raises(DatabaseConfigurationError, match="DB_PASSWORD"):
        get_db_config()


@pytest.mark.parametrize("port", ["not-a-port", "0", "65536"])
def test_invalid_database_port_is_rejected(monkeypatch, port):
    monkeypatch.setenv("DB_USER", "test_user")
    monkeypatch.setenv("DB_PASSWORD", "test-only-unused")
    monkeypatch.setenv("DB_PORT", port)
    with pytest.raises(DatabaseConfigurationError, match="DB_PORT"):
        get_db_config()
