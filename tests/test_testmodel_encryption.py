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

def test_encrypted_model_auto_decrypt(app):
    record = TestModel(ext_id="tm-6001", title="Auto Decrypt Test")
    record.set_encrypted_fields(
        secret_app="coupon: TAU-222",
        email_dbenc="tau@example.com"
    )

    db.session.add(record)
    db.session.commit()

    found = TestModel.query.filter_by(ext_id="tm-6001").first()

    # ✅ Transparent decryption
    assert found.secret_app_plain == "coupon: TAU-222"
    assert found.email_plain == "tau@example.com"
    assert found.title == "Auto Decrypt Test"
