from flask_login import UserMixin
from datetime import datetime
from app import db

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
