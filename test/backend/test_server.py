from datetime import date
from decimal import Decimal
from unittest.mock import Mock

import mysql.connector
import pytest
from fastapi.testclient import TestClient

from backend import db_helper
from backend.server import app

client = TestClient(app)


def test_save_calls_one_replacement(monkeypatch):
    replace = Mock()
    monkeypatch.setattr(db_helper, "replace_expenses_for_date", replace)
    response = client.post("/expenses/2026-09-03", json=[
        {"amount": "12.50", "category": "Food", "notes": "Sample"},
    ])
    assert response.status_code == 200
    replace.assert_called_once_with(date(2026, 9, 3), [
        {"amount": Decimal("12.50"), "category": "Food", "notes": "Sample"},
    ])


@pytest.mark.parametrize("amount", ["0", "-1", "NaN", "Infinity", "1.234", "10000000000.00"])
def test_invalid_amount_never_reaches_database(monkeypatch, amount):
    replace = Mock()
    monkeypatch.setattr(db_helper, "replace_expenses_for_date", replace)
    response = client.post("/expenses/2026-09-03", json=[
        {"amount": amount, "category": "Food", "notes": ""},
    ])
    assert response.status_code == 422
    replace.assert_not_called()


def test_invalid_category_and_long_notes_are_rejected(monkeypatch):
    replace = Mock()
    monkeypatch.setattr(db_helper, "replace_expenses_for_date", replace)
    response = client.post("/expenses/2026-09-03", json=[
        {"amount": "1.00", "category": "Unknown", "notes": "a" * 501},
    ])
    assert response.status_code == 422
    replace.assert_not_called()


def test_database_failure_never_returns_success_or_driver_details(monkeypatch):
    monkeypatch.setattr(
        db_helper, "replace_expenses_for_date",
        Mock(side_effect=mysql.connector.Error("private database connection details")),
    )
    response = client.post("/expenses/2026-09-03", json=[])
    assert response.status_code == 503
    assert response.json() == {"detail": "The database request could not be completed."}


def test_reversed_date_range_never_queries_database(monkeypatch):
    summary = Mock()
    monkeypatch.setattr(db_helper, "fetch_expense_summary", summary)
    response = client.post("/analytics/", json={
        "start_date": "2026-09-10", "end_date": "2026-09-01",
    })
    assert response.status_code == 422
    summary.assert_not_called()


def test_category_percentages_and_empty_results(monkeypatch):
    summary = Mock(return_value=[
        {"category": "Food", "total": Decimal("30.00")},
        {"category": "Other", "total": Decimal("10.00")},
    ])
    monkeypatch.setattr(db_helper, "fetch_expense_summary", summary)
    payload = {"start_date": "2026-09-01", "end_date": "2026-09-30"}
    response = client.post("/analytics/", json=payload)
    assert response.status_code == 200
    assert response.json()["Food"] == {"total": 30.0, "percentage": 75.0}
    summary.return_value = []
    assert client.post("/analytics/", json=payload).json() == {}


def test_expense_serialization_and_empty_day(monkeypatch):
    fetch = Mock(return_value=[
        {"amount": Decimal("12.50"), "category": "Food", "notes": "Sample"},
    ])
    monkeypatch.setattr(db_helper, "fetch_expenses_for_date", fetch)
    response = client.get("/expenses/2026-09-03")
    assert response.status_code == 200
    assert response.json()[0]["amount"] == "12.50"
    fetch.return_value = []
    assert client.get("/expenses/2026-09-04").json() == []
