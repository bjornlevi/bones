import os
import json
import base64
import pytest
from sqlalchemy.orm import scoped_session, sessionmaker
from app import create_app, db as _db

@pytest.fixture(scope="session")
def app():
    """Create a Flask app configured for testing with fake secrets."""
    # Fake secrets so Config.validate() passes
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["APP_ENCRYPTION_KEY"] = base64.urlsafe_b64encode(os.urandom(32)).decode()
    os.environ["KEYRING_PATH"] = "./tests/test-keyring.json"

    # Create a fake test keyring file
    key = base64.urlsafe_b64encode(os.urandom(32)).decode()
    os.makedirs(os.path.dirname(os.environ["KEYRING_PATH"]), exist_ok=True)
    with open(os.environ["KEYRING_PATH"], "w") as f:
        json.dump({"active": "v1", "keys": {"v1": key}}, f, indent=2)

    # Create test app
    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    with app.app_context():
        yield app

@pytest.fixture(scope="session")
def db(app):
    """Provide a database for tests."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()

@pytest.fixture(scope="function", autouse=True)
def session(db):
    """Provide a fresh DB session for each test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    # Create a scoped session factory
    Session = scoped_session(sessionmaker(bind=connection))
    db.session = Session

    yield Session

    # Roll back everything after each test
    transaction.rollback()
    connection.close()
    Session.remove()  # ✅ Call remove() on the scoped_session, not on a Session instance
