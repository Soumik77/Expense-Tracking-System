import pytest

from backend import db_helper


@pytest.fixture(autouse=True)
def isolate_database(monkeypatch, request):
    """Ordinary tests must never connect to a developer's real database."""
    if request.node.get_closest_marker("integration"):
        return

    def blocked_connection(**kwargs):
        raise AssertionError("Mock the database connection in unit tests.")

    monkeypatch.setattr(db_helper.mysql.connector, "connect", blocked_connection)
    monkeypatch.setattr(db_helper, "get_db_config", lambda: {})
