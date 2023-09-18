import os

import click
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.trace.samplers import ProbabilitySampler
from sqlalchemy.orm import DeclarativeBase


class BaseModel(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=BaseModel)
migrate = Migrate()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, static_folder="../static", template_folder="../templates")

    # Load configuration for prod vs. dev
    is_prod_env = "RUNNING_IN_PRODUCTION" in os.environ
    if not is_prod_env:
        app.config.from_object("flaskapp.config.development")
    else:
        app.config.from_object("flaskapp.config.production")  # pragma: no cover
        FlaskMiddleware(
            app,
            exporter=AzureExporter(connection_string=os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING", None)),
            sampler=ProbabilitySampler(rate=1.0),
        )

    # Configure the database
    if test_config is not None:
        app.config.update(test_config)

    app.config.update(SQLALCHEMY_DATABASE_URI=app.config.get("DATABASE_URI"), SQLALCHEMY_TRACK_MODIFICATIONS=False)

    db.init_app(app)
    migrate.init_app(app, db)

    from . import pages

    app.register_blueprint(pages.bp)

    @app.cli.command("seed")
    @click.option("--drop", is_flag=True, default=False)
    @click.option("--filename", default="seed_data.json")
    def seed_data(filename, drop):
        from . import seeder

        seeder.seed_data(db, filename)
        click.echo("Database seeded!")

    return app
