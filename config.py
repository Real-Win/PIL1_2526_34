import os

class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-secret-key-change-in-production"
    )

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///mentorlink.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SITE_URL = os.environ.get(
        "SITE_URL",
        "https://rising-minds-mentorlink.onrender.com"
    )