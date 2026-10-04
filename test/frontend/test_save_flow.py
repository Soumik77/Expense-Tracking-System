from unittest.mock import Mock

import pytest
import requests
from streamlit.testing.v1 import AppTest

from frontend import api_client


@pytest.fixture
def api(monkeypatch):
    state = {"expenses": [], "get_status": 200, "post_status": 200, "saved": []}

    def request(method, url, **kwargs):
        if method == "GET" and "/expenses/" in url:
            status, data = state["get_status"], state["expenses"]
        elif method == "POST" and "/expenses/" in url:
            state["saved"].append(kwargs["json"])
            status, data = state["post_status"], {"message": "saved"}
        elif url.endswith("/summary/"):
            status, data = 200, []
        else:
            raise AssertionError(f"Unexpected request: {method} {url}")
        return Mock(status_code=status, ok=status == 200, json=lambda: data)

    monkeypatch.setattr(api_client.requests, "request", request)
    return state


def open_app():
    app = AppTest.from_file("frontend/app.py", default_timeout=15).run()
    assert not app.exception
    return app


def save_button(app):
    return next(button for button in app.button if button.label == "Save expenses")


def test_failed_post_after_successful_get_does_not_show_success(api):
    api["post_status"] = 503
    app = open_app()
    app.number_input[0].set_value(12.50)
    save_button(app).click().run()
    assert not app.exception
    assert len(api["saved"]) == 1
    assert not app.success
    assert len(app.error) == 1


def test_success_is_shown_only_after_successful_save(api):
    app = open_app()
    app.number_input[0].set_value(12.50)
    save_button(app).click().run()
    assert not app.exception
    assert len(app.success) == 1
    assert api["saved"][0][0]["amount"] == "12.50"


def test_failed_read_does_not_offer_a_destructive_empty_form(api):
    api["get_status"] = 503
    app = open_app()
    assert not any(button.label == "Save expenses" for button in app.button)
    assert not api["saved"]


def test_more_than_five_existing_rows_are_preserved(api):
    api["expenses"] = [
        {"amount": "1.00", "category": "Food", "notes": f"Sample {i}"}
        for i in range(7)
    ]
    app = open_app()
    assert len(app.number_input) == 7
    save_button(app).click().run()
    assert not app.exception
    assert len(api["saved"][0]) == 7


def test_clearing_existing_records_requires_checkbox(api):
    api["expenses"] = [{"amount": "1.00", "category": "Food", "notes": "Sample"}]
    app = open_app()
    app.number_input[0].set_value(0.0)
    save_button(app).click().run()
    assert not api["saved"]
    assert len(app.warning) == 1
    app.checkbox[0].check()
    save_button(app).click().run()
    assert api["saved"] == [[]]


@pytest.mark.parametrize("failure", [requests.Timeout, requests.ConnectionError])
def test_network_failure_is_reported_without_raw_details(monkeypatch, failure):
    monkeypatch.setattr(
        api_client.requests, "request", Mock(side_effect=failure("private connection info"))
    )
    with pytest.raises(api_client.ApiError) as exc:
        api_client.request_api("POST", "/expenses/2026-09-03", json=[])
    assert "private connection info" not in str(exc.value)
