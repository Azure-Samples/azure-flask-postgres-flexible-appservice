# ruff: noqa: F401

import os

import pytest

# Import only the tests that we want to run for smoke testing
from .test_playwright import (
    test_about,
    test_destination_options_have_cruises,
    test_destinations,
    test_home,
    test_request_information,
)


def pytest_addoption(parser):
    parser.addoption(
        "--live-server-url",
        action="store",
        default="http://localhost:8000",
        help="URL for the live server to test against",
    )


@pytest.fixture(scope="function")
def live_server_url(request):
    return request.config.getoption("--live-server-url")