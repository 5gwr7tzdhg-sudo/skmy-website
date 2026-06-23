import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY environment variable must be set.")

    ENV = os.getenv("ENV", os.getenv("FLASK_ENV", "development")).lower()
    _base_url = os.getenv("BASE_URL")
    if ENV == "production" and not _base_url:
        raise RuntimeError("BASE_URL environment variable must be set in production.")
    BASE_URL = (_base_url or "http://127.0.0.1:5000").rstrip("/")
    GA_MEASUREMENT_ID = os.getenv("GA_MEASUREMENT_ID", "").strip()

    SQLALCHEMY_DATABASE_URI = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 5432)),
        database=os.getenv("DB_NAME"),
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = ENV == "production"
