"""Opt-in tests create and remove their own uniquely named MySQL database."""

import os
import uuid
from decimal import Decimal
from pathlib import Path

import mysql.connector
import pytest
from fastapi.testclient import TestClient

from backend import db_helper
from backend.server import app

pytestmark = pytest.mark.integration


@pytest.fixture
def mysql_database(monkeypatch):
    if os.getenv("RUN_MYSQL_TESTS") != "1":
        pytest.skip("Set RUN_MYSQL_TESTS=1 and MYSQL_TEST_* for a disposable local server.")
    if not os.getenv("MYSQL_TEST_USER"):
        pytest.fail("MYSQL_TEST_USER must be supplied explicitly.")
    config = {
        "host": os.getenv("MYSQL_TEST_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_TEST_PORT", "3306")),
        "user": os.environ["MYSQL_TEST_USER"],
        "password": os.getenv("MYSQL_TEST_PASSWORD", ""),
    }
    name = "expense_test_" + uuid.uuid4().hex
    admin = mysql.connector.connect(**config, autocommit=True)
    cursor = admin.cursor()
    created = False
    try:
        cursor.execute(f"CREATE DATABASE {name}")
        created = True
        cursor.execute(f"USE {name}")
        schema = Path("database/schema.sql").read_text()
        table_statement = "CREATE TABLE" + schema.split("CREATE TABLE", 1)[1]
        cursor.execute(table_statement)
        monkeypatch.setattr(
            db_helper, "get_db_config", lambda: {**config, "database": name, "autocommit": False}
        )
        yield
    finally:
        if created:
            cursor.execute(f"DROP DATABASE {name}")
        cursor.close()
        admin.close()


def test_api_round_trip_and_reports(mysql_database):
    with TestClient(app) as client:
        for day, amount, category in [
            ("2025-09-03", "12.50", "Food"),
            ("2026-09-03", "30.00", "Food"),
            ("2026-09-04", "10.00", "Other"),
        ]:
            response = client.post(f"/expenses/{day}", json=[
                {"amount": amount, "category": category, "notes": "Synthetic sample"},
            ])
            assert response.status_code == 200
        assert client.get("/expenses/2026-09-03").json()[0]["amount"] == "30.00"
        breakdown = client.post("/analytics/", json={
            "start_date": "2026-09-01", "end_date": "2026-09-30",
        }).json()
        assert breakdown["Food"]["percentage"] == 75.0
        monthly = client.get("/summary/").json()
        assert monthly == [
            {"month": "2025-09", "total_expense": 12.5},
            {"month": "2026-09", "total_expense": 40.0},
        ]


def test_failed_insert_preserves_original_day(mysql_database):
    db_helper.insert_expense("2026-09-03", Decimal("12.50"), "Food", "Original sample")
    with pytest.raises(mysql.connector.Error):
        db_helper.replace_expenses_for_date("2026-09-03", [
            {"amount": Decimal("3.00"), "category": "Food", "notes": "Valid sample"},
            {"amount": Decimal("-1.00"), "category": "Food", "notes": "Reject sample"},
        ])
    rows = db_helper.fetch_expenses_for_date("2026-09-03")
    assert len(rows) == 1
    assert rows[0]["amount"] == Decimal("12.50")
    assert rows[0]["notes"] == "Original sample"


def test_clear_one_day_preserves_other_day_and_literal_notes(mysql_database):
    note = "Sample'); DROP TABLE expenses; --"
    db_helper.insert_expense("2026-09-03", Decimal("12.50"), "Food", "Sample")
    db_helper.insert_expense("2026-09-04", Decimal("5.00"), "Other", note)
    db_helper.replace_expenses_for_date("2026-09-03", [])
    assert db_helper.fetch_expenses_for_date("2026-09-03") == []
    remaining = db_helper.fetch_expenses_for_date("2026-09-04")
    assert len(remaining) == 1
    assert remaining[0]["notes"] == note
