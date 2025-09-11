from sqlalchemy.types import TypeDecorator, Text
from cryptography.fernet import InvalidToken
from app.security.keyring import active_kid_and_fernet, column_fernet_for, wrap_ciphertext, unwrap_ciphertext

class EncryptedText(TypeDecorator):
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Encrypt before saving."""
        if value is None:
            return None

        kid, fernet = active_kid_and_fernet()
        token = fernet.encrypt(value.encode()).decode()
        return wrap_ciphertext(kid, token)

    def process_result_value(self, value, dialect):
        """Decrypt when reading."""
        if value is None:
            return None

        if not value.startswith("enc::"):
            # If somehow plaintext was stored, just return it
            return value

        try:
            kid, token = unwrap_ciphertext(value)
            fernet = column_fernet_for(kid)
            return fernet.decrypt(token.encode()).decode()
        except (InvalidToken, ValueError):
            raise ValueError("Unable to decrypt column value")
