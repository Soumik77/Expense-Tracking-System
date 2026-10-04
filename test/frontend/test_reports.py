from unittest.mock import Mock

from streamlit.testing.v1 import AppTest

from frontend import api_client


def test_populated_monthly_report_keeps_years_in_chronological_order(monkeypatch):
    def request(method, url, **kwargs):
        data = []
        if url.endswith('/summary/'):
            data = [
                {'month': '2026-01', 'total_expense': 10.0},
                {'month': '2025-12', 'total_expense': 20.0},
            ]
        return Mock(status_code=200, ok=True, json=lambda: data)

    monkeypatch.setattr(api_client.requests, 'request', request)
    app = AppTest.from_file('frontend/app.py', default_timeout=15).run()
    assert not app.exception
    assert app.table[0].value['Month'].tolist() == ['2025-12', '2026-01']
    assert app.table[0].value['Total'].tolist() == [20.0, 10.0]


def test_category_report_renders_totals_and_percentages(monkeypatch):
    def request(method, url, **kwargs):
        data = []
        if url.endswith('/analytics/'):
            data = {
                'Other': {'total': 10, 'percentage': 25},
                'Food': {'total': 30, 'percentage': 75},
            }
        return Mock(status_code=200, ok=True, json=lambda: data)

    monkeypatch.setattr(api_client.requests, 'request', request)
    app = AppTest.from_file('frontend/app.py', default_timeout=15).run()
    next(button for button in app.button if button.label == 'Get analytics').click().run()
    assert not app.exception
    assert app.table[0].value['Category'].tolist() == ['Food', 'Other']
    assert app.table[0].value['Percentage'].tolist() == [75.0, 25.0]
