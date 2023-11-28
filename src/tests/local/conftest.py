import os
import pathlib
from multiprocessing import Process

import ephemeral_port_reserve
import pytest
from flask import Flask

from flaskapp import create_app, db, seeder


def run_server(app: Flask, port: int):
    app.run(port=port, debug=False)


@pytest.fixture(scope="session")
def app_with_db():
    """Session-wide test `Flask` application."""
    config_override = {
        "TESTING": True,
        # Allows for override of database to separate test from dev environments
        "SQLALCHEMY_DATABASE_URI": os.environ.get("TEST_DATABASE_URL", os.environ.get("DATABASE_URI")),
    }
    app = create_app(config_override)

    with app.app_context():
        engines = db.engines
        db.create_all()
        seeder.seed_data(db, pathlib.Path(__file__).parent.parent.parent / "seed_data.json")

    engine_cleanup = []

    for key, engine in engines.items():
        connection = engine.connect()
        transaction = connection.begin()
        engines[key] = connection
        engine_cleanup.append((key, engine, connection, transaction))

    yield app

    for key, engine, connection, transaction in engine_cleanup:
        transaction.rollback()
        connection.close()
        engines[key] = engine


@pytest.fixture(scope="session")
def live_server_url(app_with_db):
    """Returns the url of the live server"""

    # Start the process
    hostname = ephemeral_port_reserve.LOCALHOST
    free_port = ephemeral_port_reserve.reserve(hostname)
    proc = Process(
        target=run_server,
        args=(
            app_with_db,
            free_port,
        ),
        daemon=True,
    )
    proc.start()

    # Return the URL of the live server
    yield f"http://{hostname}:{free_port}"

    # Clean up the process
    proc.kill()
