# scripts/reencrypt.py
from app import create_app, db
from app.models.user import User
from app.security.keyring import active_kid_and_fernet, unwrap_ciphertext, wrap_ciphertext, column_fernet_for

app = create_app()
with app.app_context():
    new_kid, new_f = active_kid_and_fernet()
    for u in User.query.yield_per(500):
        # force re-bind by setting same value; ORM will encrypt with active key
        u.email = u.email
        u.phone = u.phone
    db.session.commit()
