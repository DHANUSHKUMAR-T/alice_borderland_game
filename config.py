import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Secret key for sessions
    SECRET_KEY = os.environ.get("SECRET_KEY") or "super-secret-key"

    # Database config (SQLite)
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        "sqlite:///" + os.path.join(BASE_DIR, "app.db")

    # Disable unnecessary warnings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
