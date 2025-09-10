from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime


db = SQLAlchemy()

class SiteUser(db.Model, UserMixin):
    __tablename__ = "site_users"

    id = db.Column(db.Integer, primary_key=True)
    auth_user_id = db.Column(db.Integer, nullable=False, unique=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120))
    role = db.Column(db.String(50), default="user")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"{self.username} - {self.email} - {self.role}"

class TestModel(db.Model):
    __tablename__ = "TestModel"

    id = db.Column(db.Integer, primary_key=True)
    ext_id = db.Column(db.String(64), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)

    # 🔐 App-level encrypted secret (AES-GCM)
    secret_app = db.Column(db.LargeBinary, nullable=False)

    # 🔐 MySQL column-level encrypted email (AES_ENCRYPT)
    email_dbenc = db.Column(db.LargeBinary, nullable=False)

    created_at = db.Column(
        db.TIMESTAMP,
        nullable=False,
        server_default=db.text("CURRENT_TIMESTAMP")
    )

    def __repr__(self):
        return f"<TestModel id={self.id} title={self.title}>"