import os
import json
import sys

# ✅ Ensure the project root is added to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.services import test_model_service

def ingest_test_models():
    app = create_app()
    with app.app_context():
        dummy_path = os.path.join("tests", "data", "test_model_dummy.json")
        if not os.path.exists(dummy_path):
            raise FileNotFoundError(f"Missing dummy data: {dummy_path}")

        with open(dummy_path) as f:
            records = json.load(f)

        for rec in records:
            test_model_service.create_test_model(
                ext_id=rec["ext_id"],
                title=rec["title"],
                email=rec["email"],
                secret=rec["secret"]
            )

        print(f"✅ Inserted {len(records)} encrypted TestModel records")

if __name__ == "__main__":
    ingest_test_models()
