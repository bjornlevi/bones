import ssl
import pymysql
from app.config import Config
import os
from app.models import db, TestModel
from app.crypto.keystore import load_or_create, get_plain_app_dek, get_plain_dbcol_key
from app.crypto.appenc import encrypt, decrypt


def _db():
    """Create a DB connection for AES_ENCRYPT/AES_DECRYPT usage."""
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

def create_test_model(ext_id: str, title: str, email: str, secret: str):
    """Insert a new encrypted record into TestModel."""
    keys = load_or_create()
    app_dek = get_plain_app_dek(keys)
    dbcol_key = get_plain_dbcol_key(keys)

    secret_ciphertext = encrypt(secret.encode(), app_dek)

    conn = _db()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO TestModel (ext_id, title, secret_app, email_dbenc)
            VALUES (%s, %s, %s, AES_ENCRYPT(%s, UNHEX(SHA2(%s,512))))
            ON DUPLICATE KEY UPDATE
                title=VALUES(title),
                secret_app=VALUES(secret_app),
                email_dbenc=VALUES(email_dbenc)
            """,
            (ext_id, title, secret_ciphertext, email, dbcol_key),
        )


def get_test_model_by_id(record_id: int):
    """Fetch a record by ID and decrypt fields."""
    keys = load_or_create()
    app_dek = get_plain_app_dek(keys)
    dbcol_key = get_plain_dbcol_key(keys)

    conn = _db()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, ext_id, title, secret_app,
            CAST(AES_DECRYPT(email_dbenc, UNHEX(SHA2(%s,512))) AS CHAR) AS email_plain
            FROM TestModel
            WHERE id=%s
            """,
            (dbcol_key, record_id),
        )
        row = cur.fetchone()
        if not row:
            return None

        row["secret_plain"] = decrypt(row["secret_app"], app_dek).decode()
        del row["secret_app"]
        return row


def list_test_models(limit=20):
    """List encrypted records and return decrypted values."""
    keys = load_or_create()
    app_dek = get_plain_app_dek(keys)
    dbcol_key = get_plain_dbcol_key(keys)

    conn = _db()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, ext_id, title, secret_app,
            CAST(AES_DECRYPT(email_dbenc, UNHEX(SHA2(%s,512))) AS CHAR) AS email_plain
            FROM TestModel
            ORDER BY id DESC
            LIMIT %s
            """,
            (dbcol_key, limit),
        )
        rows = cur.fetchall()
        for r in rows:
            r["secret_plain"] = decrypt(r["secret_app"], app_dek).decode()
            del r["secret_app"]
        return rows
