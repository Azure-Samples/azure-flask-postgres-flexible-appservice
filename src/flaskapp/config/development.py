import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = True

dbuser = os.environ["POSTGRES_USERNAME"]
dbpass = os.environ["POSTGRES_PASSWORD"]
dbhost = os.environ["POSTGRES_HOST"]
dbname = os.environ["POSTGRES_DATABASE"]
dbport = os.environ.get("POSTGRES_PORT", 5432)
DATABASE_URI = f"postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}:{dbport}/{dbname}"

TIME_ZONE = "UTC"
