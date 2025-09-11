from app.security.keyring import app_fernet

def encrypt_secret(s: str) -> str:
    return app_fernet().encrypt(s.encode()).decode()

def decrypt_secret(t: str) -> str:
    return app_fernet().decrypt(t.encode()).decode()
