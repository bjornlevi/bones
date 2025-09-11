from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema
from typing import Any
from app.security.keyring import get_column_encrypter

def _fernet():
    return get_column_encrypter()

class EncryptedStr(str):
    """Custom type that encrypts values transparently."""

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler):
        def encrypt_value(value: str) -> str:
            if value is None:
                return None
            return _fernet().encrypt(value.encode()).decode()
        return core_schema.no_info_after_validator_function(encrypt_value, core_schema.str_schema())

    @staticmethod
    def decrypt(value: str) -> str:
        return _fernet().decrypt(value.encode()).decode()
