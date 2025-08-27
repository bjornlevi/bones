import os

class Config:
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.environ.get('MYSQL_USER')}:{os.environ.get('MYSQL_PASSWORD')}"
        f"@{os.environ.get('MYSQL_HOST')}/{os.environ.get('MYSQL_DATABASE')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL")
    AUTH_SERVICE_API_KEY = os.environ.get("AUTH_SERVICE_API_KEY")

    SECRET_KEY = os.environ.get("SECRET_KEY", "changeme")
    SESSION_TYPE = os.environ.get("SESSION_TYPE", "filesystem")

    SITE_NAME = os.environ.get("SITE_NAME", "site")
    DEFAULT_SITE_ADMIN_PASS = os.environ.get("DEFAULT_SITE_ADMIN_PASS", "changeme")
