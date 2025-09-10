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
    SITE_ADMIN_PASSWORD = os.environ.get("SITE_ADMIN_PASSWORD", "changeme")

    # 🔐 Vault KMS settings
    VAULT_ADDR = os.getenv("VAULT_ADDR", "http://vault:8200")
    VAULT_TOKEN = os.getenv("VAULT_TOKEN", "root")
    VAULT_TRANSIT_MOUNT = os.getenv("VAULT_TRANSIT_MOUNT", "transit")
    VAULT_APP_KEY_NAME = os.getenv("VAULT_APP_KEY_NAME", "bones-app-master")
    VAULT_DBCOL_KEY_NAME = os.getenv("VAULT_DBCOL_KEY_NAME", "bones-dbcol-master")
