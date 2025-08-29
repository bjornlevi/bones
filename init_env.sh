#!/usr/bin/env bash
# init_env.sh - Generate a .env file with secure random values for bones site

set -e

ENV_FILE=".env"

if [ -f "$ENV_FILE" ]; then
  echo "⚠️  $ENV_FILE already exists. Remove it first if you want to regenerate."
  exit 1
fi

# Generate secure random values
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
MYSQL_PASSWORD=$(python3 -c 'import secrets; print(secrets.token_urlsafe(16))')
MYSQL_ROOT_PASSWORD=$(python3 -c 'import secrets; print(secrets.token_urlsafe(16))')
SITE_ADMIN_PASSWORD=$(python3 -c 'import secrets; print(secrets.token_urlsafe(16))')

cat > $ENV_FILE <<EOL
# =============================
# Bones Site Environment Config
# =============================

# MySQL
MYSQL_DATABASE=barebones
MYSQL_USER=bareuser
MYSQL_PASSWORD=${MYSQL_PASSWORD}
MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
MYSQL_HOST=db

# Flask
FLASK_ENV=development
SECRET_KEY=${SECRET_KEY}

# Site identity
SITE_NAME=Bones

# Site admin bootstrap (default admin name SITE_NAME_admin)
SITE_ADMIN_PASSWORD=${SITE_ADMIN_PASSWORD}

# Auth service connection
AUTH_SERVICE_URL=http://auth-service:5000/auth
AUTH_SERVICE_API_KEY=replace_with_auth_service_key
EOL

echo "✅ $ENV_FILE created with secure random values."
echo "   Site admin = site_admin / ${SITE_ADMIN_PASSWORD}"
