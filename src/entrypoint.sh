#!/bin/bash
set -e
python3 -m pip install --upgrade pip
python3 -m pip install -e .
python3 -m flask --app flaskapp db upgrade --directory flaskapp/migrations
python3 -m flask --app flaskapp seed --filename="seed_data.json"
python3 -m gunicorn "flaskapp:create_app()"
