from sqlalchemy import text
from app.models.demo_model import DemoModel

def test_encryption_and_decryption(db, session):
    demo = DemoModel(email="alice@example.com", phone="123456789")
    session.add(demo)
    session.commit()

    loaded = session.query(DemoModel).filter_by(id=demo.id).first()
    assert loaded.email == "alice@example.com"
    assert loaded.phone == "123456789"

    raw_email = session.execute(
        text("SELECT email FROM demo_model WHERE id=:id"),
        {"id": demo.id},
    ).scalar()
    assert raw_email != "alice@example.com"
    assert raw_email.startswith("enc::")
