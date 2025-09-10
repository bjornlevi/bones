init:
	./init_env.sh

check-net:
	@if ! docker network ls --format '{{.Name}}' | grep -q '^authnet$$'; then \
		echo "❌ Network 'authnet' not found. Please run 'make up' in auth-service first."; \
		exit 1; \
	fi

up: check-net
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f web

shell:
	docker compose exec web flask shell

test:
	docker compose run --rm web pytest -v tests

# Flask-only shortcuts
fdown:
	docker compose stop web && docker compose rm -f web

fup:
	docker compose up --build -d web

reset: down
	@echo "⚠️  Removing .env and DB volumes to start fresh..."
	@rm -f .env
	@docker volume rm $$(docker volume ls -q | grep bones_site-db-data) || true
	@echo "✅ Reset complete. Run 'make init' to create a new .env."

# ----------------------------
# 🔐 Encryption Additions
# ----------------------------

migrate:
	docker compose exec database sh -lc "mysql -uroot -p$$MYSQL_ROOT_PASSWORD $$MYSQL_DATABASE < /app/migrations/001_init.sql"

ingest:
	REMOTE_URL=$${REMOTE_URL:-file:///app/tests/data/dummy.json} docker compose exec app python scripts/ingest.py

vault-init:
	@echo "🔐 Initializing Vault Transit Engine..."
	docker compose exec vault sh -lc 'export VAULT_ADDR=$$VAULT_ADDR && \
		vault secrets enable -path=$$VAULT_TRANSIT_MOUNT transit || true && \
		vault write -f $$VAULT_TRANSIT_MOUNT/keys/$$VAULT_APP_KEY_NAME || true && \
		vault write -f $$VAULT_TRANSIT_MOUNT/keys/$$VAULT_DBCOL_KEY_NAME || true'
	@echo "✅ Vault Transit keys initialized"

.PHONY: up down logs shell test fdown fup reset migrate ingest vault-init
