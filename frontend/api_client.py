import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")


class ApiError(RuntimeError):
    """A request could not be completed or its response was invalid."""


def request_api(method, path, **kwargs):
    try:
        response = requests.request(method, f"{API_URL}{path}", timeout=10, **kwargs)
    except requests.Timeout:
        raise ApiError(
            "The server did not respond in time. Reload the records before retrying a save."
        ) from None
    except requests.RequestException:
        raise ApiError("Cannot reach the server. Check that the backend is running.") from None

    if response.status_code == 422:
        raise ApiError("Check the amounts, categories, notes, and selected dates.")
    if not response.ok:
        raise ApiError("The server could not complete the request. Please try again.")
    try:
        return response.json()
    except ValueError:
        raise ApiError("The server returned an unreadable response.") from None
