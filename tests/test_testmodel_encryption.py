import os
import pymysql
import pytest
import sys

# ✅ Ensure project root is on sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.services import test_model_service

@pytest.fixture(scope="module")
def app():
    """Set up Flask app for testing."""
    app = create_app()
    with app.app_context():
        yield app

@pytest.fixture(scope="module")
def db_conn():
    """Direct raw connection to MySQL to verify encrypted columns."""
    conn = pymysql.connect(
        host=os.getenv("MYSQL_HOST", "db"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        port=int(os.getenv("DB_PORT", "3306")),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )
    yield conn
    conn.close()

def test_testmodel_insert_and_encryption(app, db_conn):
    """Insert an encrypted record and validate storage + decryption."""

    # 1️⃣ Insert a record
    ext_id = "tm-9999"
    title = "Vault Test Model"
    email = "vaulttest@example.com"
    secret = "coupon: SECURE-999"

    test_model_service.create_test_model(
        ext_id=ext_id,
        title=title,
        email=email,
        secret=secret,
    )

    # 2️⃣ Query DB directly to confirm email_dbenc is encrypted
    with db_conn.cursor() as cur:
        cur.execute("SELECT email_dbenc, secret_app FROM TestModel WHERE ext_id=%s", (ext_id,))
        row = cur.fetchone()

    assert row, "Record should exist in DB"
    assert isinstance(row["email_dbenc"], bytes), "Email should be stored encrypted"
    assert isinstance(row["secret_app"], bytes), "Secret should be stored encrypted"
    assert secret.encode() not in row["secret_app"], "Secret must not be stored in plaintext"

    # 3️⃣ Fetch decrypted record via service
    decrypted = test_model_service.get_test_model_by_id(
        record_id=test_model_service.list_test_models()[0]["id"]
    )

    assert decrypted["secret_plain"] == secret, "Decrypted secret must match"
    assert decrypted["email_plain"] == email, "Decrypted email must match"
