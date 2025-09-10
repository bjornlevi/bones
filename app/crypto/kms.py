import base64
import hvac
from app.config import Config
from dataclasses import dataclass

@dataclass
class WrappedKey:
    ciphertext: bytes
    key_id: str

class KMS:
    @staticmethod
    def _client():
        return hvac.Client(url=Config.VAULT_ADDR, token=Config.VAULT_TOKEN)

    @staticmethod
    def generate_dek():
        """Generate a 256-bit DEK (Data Encryption Key)."""
        return base64.b64encode(hvac.utils.generate_random_bytes(32))

    @staticmethod
    def wrap(key: bytes, which: str) -> WrappedKey:
        client = KMS._client()
        key_name = Config.VAULT_APP_KEY_NAME if which == "app" else Config.VAULT_DBCOL_KEY_NAME

        resp = client.secrets.transit.encrypt_data(
            name=key_name,
            plaintext=base64.b64encode(key).decode(),
            mount_point=Config.VAULT_TRANSIT_MOUNT,
        )
        return WrappedKey(resp["data"]["ciphertext"].encode(), key_name)

    @staticmethod
    def unwrap(wrapped: WrappedKey) -> bytes:
        client = KMS._client()
        resp = client.secrets.transit.decrypt_data(
            name=wrapped.key_id,
            ciphertext=wrapped.ciphertext.decode(),
            mount_point=Config.VAULT_TRANSIT_MOUNT,
        )
        return base64.b64decode(resp["data"]["plaintext"])
