import ssl, pymysql
from config import settings
from app.crypto.keystore import load_or_create, get_plain_app_dek, get_plain_dbcol_key
from app.crypto.appenc import decrypt

def _db():
    ctx = ssl.create_default_context()
    return pymysql.connect(
        host=settings.DB_HOST,
        user=settings.DB_USER,
        password=settings.DB_PASS,
        database=settings.DB_NAME,
        port=settings.DB_PORT,
        ssl=ctx,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )

def get_item_by_id(item_id: int):
    keys = load_or_create()
    app_dek = get_plain_app_dek(keys)
    dbcol_key = get_plain_dbcol_key(keys)
    with _db().cursor() as cur:
        cur.execute(
            "SELECT id, ext_id, title, secret_app,"
            " CAST(AES_DECRYPT(email_dbenc, UNHEX(SHA2(%s,512))) AS CHAR) AS email_plain"
            " FROM items WHERE id=%s",
            (dbcol_key, item_id)
        )
        row = cur.fetchone()
        if not row:
            return None
        row["secret_plain"] = decrypt(row["secret_app"], app_dek).decode()
        del row["secret_app"]
        return row

def list_items(limit=50):
    keys = load_or_create()
    app_dek = get_plain_app_dek(keys)
    dbcol_key = get_plain_dbcol_key(keys)
    with _db().cursor() as cur:
        cur.execute(
            "SELECT id, ext_id, title, secret_app,"
            " CAST(AES_DECRYPT(email_dbenc, UNHEX(SHA2(%s,512))) AS CHAR) AS email_plain"
            " FROM items ORDER BY id DESC LIMIT %s",
            (dbcol_key, limit)
        )
        rows = cur.fetchall()
        for r in rows:
            r["secret_plain"] = decrypt(r["secret_app"], app_dek).decode()
            del r["secret_app"]
        return rows
