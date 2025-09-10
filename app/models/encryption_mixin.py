import os
import pymysql
from sqlalchemy.orm import declared_attr
from sqlalchemy import Column, LargeBinary
from app.crypto.keystore import load_or_create, get_plain_app_dek, get_plain_dbcol_key
from app.crypto.appenc import encrypt, decrypt

def _db():
    """Helper: direct connection to MySQL for AES_ENCRYPT/AES_DECRYPT."""
    require_ssl = os.getenv("MYSQL_REQUIRE_SSL", "false").lower() == "true"
    ssl_params = {"ssl": {}} if require_ssl else None

    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "db"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        port=int(os.getenv("DB_PORT", "3306")),
        ssl=ssl_params,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )

class EncryptedMixin:
    """Transparent Vault + MySQL column-level encryption for SQLAlchemy models."""

    __encrypted_fields__ = []  # Override this in each model, e.g. ["secret_app", "email_dbenc"]

    @declared_attr
    def secret_app(cls):
        return Column(LargeBinary, nullable=False)

    @declared_attr
    def email_dbenc(cls):
        return Column(LargeBinary, nullable=False)

    def set_encrypted_fields(self, **kwargs):
        """Encrypt fields before saving."""
        keys = load_or_create()
        app_dek = get_plain_app_dek(keys)
        dbcol_key = get_plain_dbcol_key(keys)
        conn = _db()

        with conn.cursor() as cur:
            for field, value in kwargs.items():
                if field == "secret_app":
                    setattr(self, field, encrypt(value.encode(), app_dek))
                elif field == "email_dbenc":
                    cur.execute(
                        "SELECT AES_ENCRYPT(%s, UNHEX(SHA2(%s,512))) AS encrypted",
                        (value, dbcol_key),
                    )
                    setattr(self, field, cur.fetchone()["encrypted"])

    def _decrypt_field(self, field):
        """Decrypt a single field value."""
        value = getattr(self, field)
        if value is None:
            return None

        keys = load_or_create()
        app_dek = get_plain_app_dek(keys)
        dbcol_key = get_plain_dbcol_key(keys)

        if field == "secret_app":
            return decrypt(value, app_dek).decode()

        if field == "email_dbenc":
            conn = _db()
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT CAST(AES_DECRYPT(%s, UNHEX(SHA2(%s,512))) AS CHAR) AS decrypted",
                    (value, dbcol_key),
                )
                return cur.fetchone()["decrypted"]

    def __getattr__(self, name):
        """
        Dynamically provide `<field>_plain` properties.
        Example: `record.secret_app_plain` or `record.email_plain`.
        """
        if name.endswith("_plain"):
            field = name.replace("_plain", "")
            if field in self.__encrypted_fields__:
                return self._decrypt_field(field)
        raise AttributeError(f"{self.__class__.__name__} has no attribute '{name}'")
