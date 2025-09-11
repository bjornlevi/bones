#!/usr/bin/env bash
# init_env.sh - Generate a .env file and manage MySQL credentials safely
set -e

ENV_FILE=".env"
LOCAL_KEYRING_PATH="./keys/dev-keyring.json"
CONTAINER_KEYRING_PATH="/app/keys/dev-keyring.json"
DOCKER_VOLUME="bones-encryted_site-db-data"  # <-- Change if your project name differs

if [ -f "$ENV_FILE" ]; then
  echo "⚠️  $ENV_FILE already exists. Remove it first if you want to regenerate."
  exit 1
fi

# Generate secure random values
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
MYSQL_PASSWORD=$(python3 -c 'import secrets; print(secrets.token_urlsafe(16))')
MYSQL_ROOT_PASSWORD=$(python3 -c 'import secrets; print(secrets.token_urlsafe(16))')
SITE_ADMIN_PASSWORD=$(python3 -c 'import secrets; print(secrets.token_urlsafe(16))')

# Generate encryption keys (Fernet-compatible, base64)
APP_ENCRYPTION_KEY=$(python3 -c 'import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())')
COLUMN_ENCRYPTION_KEY=$(python3 -c 'import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())')

# Write the .env file
cat > "$ENV_FILE" <<EOL
# =============================
# Bones Site Environment Config
# =============================

MYSQL_DATABASE=barebones
MYSQL_USER=bareuser
MYSQL_PASSWORD=${MYSQL_PASSWORD}
MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
MYSQL_HOST=db
MYSQL_REQUIRE_SSL=false

FLASK_ENV=development
SECRET_KEY=${SECRET_KEY}

SITE_NAME=Bones
SITE_ADMIN_PASSWORD=${SITE_ADMIN_PASSWORD}

AUTH_SERVICE_URL=http://auth-service:5000/api
AUTH_SERVICE_API_KEY=replace_with_auth_service_key

# Path inside container
KEYRING_PATH=${CONTAINER_KEYRING_PATH}

APP_ENCRYPTION_KEY=${APP_ENCRYPTION_KEY}
COLUMN_ENCRYPTION_KEY=${COLUMN_ENCRYPTION_KEY}
EOL

# Create the local keyring directory and file if missing
mkdir -p "$(dirname "$LOCAL_KEYRING_PATH")"
if [ ! -f "$LOCAL_KEYRING_PATH" ]; then
    python3 - <<PY
import os, json, base64

path = "${LOCAL_KEYRING_PATH}"
key = base64.urlsafe_b64encode(os.urandom(32)).decode()
data = {"active": "v1", "keys": {"v1": key}}
os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, "w") as f:
    json.dump(data, f, indent=2)
PY
fi

# -----------------------------------------
# Check for existing MySQL volume conflicts
# -----------------------------------------
if docker volume inspect "$DOCKER_VOLUME" >/dev/null 2>&1; then
    echo "⚠️  MySQL volume '$DOCKER_VOLUME' already exists."
    echo "   If you've changed MYSQL_PASSWORD or MYSQL_ROOT_PASSWORD,"
    echo "   you must reset the database before starting the containers:"
    echo ""
    echo "   docker compose down -v"
    echo "   docker volume rm $DOCKER_VOLUME"
    echo "   make init"
    echo ""
fi

echo "✅ $ENV_FILE created successfully."
echo "🔑 Keyring created at ${LOCAL_KEYRING_PATH}"
echo "💡 If MySQL login fails, reset the volume as shown above."
