import os
import pathlib
import socket
import time
from multiprocessing import Process

import pytest
import requests

from flaskapp import create_app, db, seeder


def wait_for_server_ready(
    url: str, timeout: float = 10.0, check_interval: float = 0.5
) -> bool:
    """Make requests to provided url until it responds without error."""
    conn_error = None
    for _ in range(int(timeout / check_interval)):
        try:
            requests.get(url)
        except requests.ConnectionError as exc:
            time.sleep(check_interval)
            conn_error = str(exc)
        else:
            return True
    raise RuntimeError(conn_error)


def free_port() -> int:
    """
    Return a free port on localhost
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        addr = s.getsockname()
        port = addr[1]
        return port


def run_server(app, port):
    app.run(port=port, debug=False)


@pytest.fixture(scope="session")
def live_server_url():
    """Returns the url of the live server"""

    # Set up the Flask app and database
    config_override = {
        "TESTING": True,
        # Allows for override of database to separate test from dev environments
        "SQLALCHEMY_DATABASE_URI": os.environ.get(
            "TEST_DATABASE_URL", os.environ.get("DATABASE_URI")
        ),
    }
    app = create_app(config_override)

    with app.app_context():
        engines = db.engines
        db.create_all()
        seeder.seed_data(
            db, pathlib.Path(__file__).parent.parent.parent / "seed_data.json"
        )

    engine_cleanup = []
    for key, engine in engines.items():
        connection = engine.connect()
        transaction = connection.begin()
        engines[key] = connection
        engine_cleanup.append((key, engine, connection, transaction))

    # Start the process
    port = free_port()
    proc = Process(
        target=run_server,
        args=(
            app,
            port,
        ),
        daemon=True,
    )
    proc.start()

    # Return the URL once server is ready
    url = f"http://localhost:{port}"
    wait_for_server_ready(url, timeout=10.0, check_interval=0.5)
    yield url

    # Clean up the database connections
    for key, engine, connection, transaction in engine_cleanup:
        transaction.rollback()
        connection.close()
        engines[key] = engine

    # Clean up the process
    proc.kill()
