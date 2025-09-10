from app import db
from app.models.encryption_mixin import EncryptedMixin

class TestModel(EncryptedMixin, db.Model):
    __tablename__ = "TestModel"
    __encrypted_fields__ = ["secret_app", "email_dbenc"]  # Enable auto-decryption

    id = db.Column(db.Integer, primary_key=True)
    ext_id = db.Column(db.String(64), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<TestModel id={self.id} title={self.title}>"
