# ruff: noqa: F401

import os

import pytest

from .test_playwright import (
    test_about,
    test_destination_options_have_cruises,
    test_destinations,
    test_home,
    test_request_information,
)


@pytest.fixture(scope="function")
def live_server_url():
    return os.environ.get("LIVE_SERVER_URL", "http://localhost:8000")
