from app import db
from app.security.sqlalchemy_types import EncryptedText

class DemoModel(db.Model):  # ✅ Correct: only inherit from db.Model
    __tablename__ = "demo_model"  # lowercase + underscores recommended

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(EncryptedText, nullable=False, unique=False)
    phone = db.Column(EncryptedText, nullable=True)
