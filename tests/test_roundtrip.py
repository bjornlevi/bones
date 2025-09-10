import pymysql, ssl
from config import settings
from app.services.items import get_item_by_id, list_items

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

def test_roundtrip():
    rows = list_items(limit=1)
    assert len(rows) >= 1
    r0 = rows[0]
    assert r0["email_plain"].endswith("@example.org")
    assert r0["secret_plain"].startswith("coupon:")

def test_direct_id():
    with _db().cursor() as cur:
        cur.execute("SELECT id FROM items ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        assert row is not None
        item = get_item_by_id(row["id"])
        assert item["email_plain"].count("@") == 1
        assert "coupon:" in item["secret_plain"]
