import os
import json
import base64
from app.crypto.kms import KMS, WrappedKey

STORE = "app/keys/state.json"

def load_or_create():
    """Get wrapped DEKs from local state or generate new ones via Vault Transit."""
    if os.path.exists(STORE):
        with open(STORE) as f:
            j = json.load(f)
        return {
            "app": WrappedKey(base64.b64decode(j["app_wrapped"]), j["app_key_id"]),
            "dbcol": WrappedKey(base64.b64decode(j["dbcol_wrapped"]), j["dbcol_key_id"]),
        }

    # First-time setup: generate DEKs and wrap them
    app_dek = os.urandom(32)
    dbcol_dek = os.urandom(32)

    app_wrapped = KMS.wrap(app_dek, "app")
    dbcol_wrapped = KMS.wrap(dbcol_dek, "dbcol")

    os.makedirs(os.path.dirname(STORE), exist_ok=True)
    with open(STORE, "w") as f:
        json.dump({
            "app_wrapped": base64.b64encode(app_wrapped.ciphertext).decode(),
            "app_key_id": app_wrapped.key_id,
            "dbcol_wrapped": base64.b64encode(dbcol_wrapped.ciphertext).decode(),
            "dbcol_key_id": dbcol_wrapped.key_id,
        }, f)

    return {
        "app": app_wrapped,
        "dbcol": dbcol_wrapped,
    }

def get_plain_app_dek(keys):
    return KMS.unwrap(keys["app"])

def get_plain_dbcol_key(keys):
    return KMS.unwrap(keys["dbcol"])
