import os
class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-secret-key-change-in-production"
    )

    SQLALCHEMY_DATABASE_URI = "sqlite:///mentorlink.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
