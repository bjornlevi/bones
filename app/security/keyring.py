from cryptography.fernet import Fernet
from app.config import Config

def app_fernet() -> Fernet:
    """Returns Fernet encrypter for app-level secrets."""
    key = Config.APP_ENCRYPTION_KEY
    if not key:
        raise RuntimeError("APP_ENCRYPTION_KEY missing. Run `make init`.")
    return Fernet(key.encode())

def column_fernet_for(kid: str) -> Fernet:
    """Return Fernet instance for a specific key ID from the keyring."""
    data = Config.keyring()
    key = data["keys"].get(kid)
    if not key:
        raise RuntimeError(f"Missing encryption key for id '{kid}' in {Config.KEYRING_PATH}")
    return Fernet(key.encode())

def active_kid_and_fernet():
    """Return the active column key ID and its Fernet instance."""
    data = Config.keyring()
    kid = data["active"]
    return kid, column_fernet_for(kid)

def wrap_ciphertext(kid: str, token: str) -> str:
    """Format encrypted value with key ID prefix."""
    # Final format stored in DB: enc::<kid>::<token>
    return f"enc::{kid}::{token}"

def unwrap_ciphertext(value: str):
    """Extract (kid, token) from stored ciphertext."""
    if not value.startswith("enc::"):
        raise ValueError("Invalid ciphertext format")
    _, kid, token = value.split("::", 2)
    return kid, token
