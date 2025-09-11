import os
import json
from pathlib import Path

class Config:
    """Central application config with security-focused defaults."""

    # --------------------------------------------------
    # Database
    # --------------------------------------------------
    MYSQL_USER = os.getenv("MYSQL_USER", "bareuser")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_HOST = os.getenv("MYSQL_HOST", "db")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "barebones")
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --------------------------------------------------
    # Auth Service Integration
    # --------------------------------------------------
    AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL")
    AUTH_SERVICE_API_KEY = os.getenv("AUTH_SERVICE_API_KEY")

    # --------------------------------------------------
    # Flask Security & Sessions
    # --------------------------------------------------
    SECRET_KEY = os.getenv("SECRET_KEY")
    SESSION_TYPE = os.getenv("SESSION_TYPE", "filesystem")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True            # force HTTPS-only cookies
    SESSION_COOKIE_SAMESITE = "Lax"         # mitigates CSRF in most cases

    # --------------------------------------------------
    # Site Identity & Bootstrap
    # --------------------------------------------------
    SITE_NAME = os.getenv("SITE_NAME", "site")
    SITE_ADMIN_PASSWORD = os.getenv("SITE_ADMIN_PASSWORD", "changeme")

    # --------------------------------------------------
    # Encryption Keys & Keyring
    # --------------------------------------------------
    APP_ENCRYPTION_KEY = os.getenv("APP_ENCRYPTION_KEY")
    KEYRING_PATH = os.getenv("KEYRING_PATH", "/app/keys/dev-keyring.json")

    @classmethod
    def keyring(cls):
        """Loads the column encryption keyring JSON from disk."""
        path = Path(cls.KEYRING_PATH)
        if not path.exists():
            raise RuntimeError(f"Keyring file missing: {cls.KEYRING_PATH}")
        with open(path, "r") as f:
            data = json.load(f)

        # Example structure: { "active": "v1", "keys": { "v1": "<base64 key>", ... } }
        active = data.get("active")
        keys = data.get("keys", {})

        if not active or active not in keys:
            raise RuntimeError(f"Invalid keyring: missing active key '{active}'")
        return data

    @classmethod
    def active_column_key(cls):
        """Returns (kid, key) tuple for column-level encryption."""
        data = cls.keyring()
        kid = data["active"]
        key = data["keys"][kid]
        return kid, key

    # --------------------------------------------------
    # Validations
    # --------------------------------------------------
    @classmethod
    def validate(cls):
        """Ensure critical secrets exist."""
        missing = []
        for env_var in ["SECRET_KEY", "APP_ENCRYPTION_KEY"]:
            if not getattr(cls, env_var):
                missing.append(env_var)
        if missing:
            raise RuntimeError(
                f"Missing required environment variables: {', '.join(missing)}. "
                "Did you forget to run `make init`?"
            )

# Run validations immediately at import
Config.validate()
