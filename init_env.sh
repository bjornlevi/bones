#!/usr/bin/env bash
# init_env.sh - Generate a .env file with placeholder values for bones site

set -e

ENV_FILE=".env"

if [ -f "$ENV_FILE" ]; then
  echo "⚠️  $ENV_FILE already exists. Remove it first if you want to regenerate."
  exit 1
fi

cat > $ENV_FILE <<EOL
# =============================
# Bones Site Environment Config
# =============================

# MySQL
MYSQL_DATABASE=barebones
MYSQL_USER=bareuser
MYSQL_PASSWORD=barepass
MYSQL_ROOT_PASSWORD=rootpass
MYSQL_HOST=db

# Flask
FLASK_ENV=development
SECRET_KEY=replace_with_a_secret_key

# Site identity
SITE_NAME=Bones

# Auth service connection
AUTH_SERVICE_URL=http://auth-web:5000/auth
AUTH_SERVICE_API_KEY=replace_with_auth_service_key
EOL

echo "✅ $ENV_FILE created. Please edit values before running 'make up'."
