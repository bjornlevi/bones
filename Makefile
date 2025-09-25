init:
	./init_env.sh

check-nets:
	@if ! docker network ls --format '{{.Name}}' | grep -q '^authnet$$'; then \
		echo "❌ Network 'authnet' not found. Please run 'make up' in auth-service first."; \
		exit 1; \
	fi
	@if ! docker network ls --format '{{.Name}}' | grep -q '^web$$'; then \
		echo "❌ Network 'web' not found. Please start Traefik (or create the 'web' network)."; \
		exit 1; \
	fi

up: check-nets
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f bones

shell:
	docker compose exec bones sh

test:
	docker compose run --rm bones pytest -v tests

# App-only shortcuts
fdown:
	docker compose stop bones && docker compose rm -f bones

fup:
	docker compose up --build -d bones

# health checks
HOST ?= 127.0.0.1
health-authnet:
	docker run --rm --network authnet curlimages/curl:latest -si http://bones:5000/health

health-web:
	docker run --rm --network web curlimages/curl:latest -si http://traefik/bones/health

health-host:
	curl -si "http://$(HOST)/bones/health"

health-all:
	@ec=0; for t in health-authnet health-web health-host; do echo "── $$t"; $(MAKE) -s $$t || ec=1; echo; done; \
	if [ $$ec -eq 0 ]; then echo "✅ bones: ALL HEALTH CHECKS PASSED"; else echo "❌ bones: SOME HEALTH CHECKS FAILED"; fi; exit $$ec

# quick API smoke against auth-service via bones env
test-auth:
	@HOST=$${HOST:-127.0.0.1}; \
	BASE="http://$$HOST/auth-service/api"; \
	APIKEY=$$(grep '^AUTH_SERVICE_API_KEY=' .env | cut -d= -f2); \
	USER=$$(grep '^SITE_NAME=' .env | cut -d= -f2)_admin; \
	PASS=$$(grep '^SITE_ADMIN_PASSWORD=' .env | cut -d= -f2); \
	echo "→ Login to auth-service as $$USER"; \
	TOKEN=$$(curl -s -X POST "$$BASE/login" -H "Content-Type: application/json" -H "X-API-Key: $$APIKEY" -d "{\"username\":\"$$USER\",\"password\":\"$$PASS\"}" | jq -r .token); \
	test -n "$$TOKEN" -a "$$TOKEN" != "null" || { echo "❌ login failed"; exit 1; }; \
	echo "→ userinfo"; curl -s -X POST "$$BASE/userinfo" -H "Content-Type: application/json" -H "X-API-Key: $$APIKEY" -d "{\"token\":\"$$TOKEN\"}" | jq .; \
	echo "→ verify";   curl -s -X POST "$$BASE/verify"   -H "Content-Type: application/json" -H "X-API-Key: $$APIKEY" -d "{\"token\":\"$$TOKEN\"}" | jq .

reset: down
	@echo "⚠️  Removing .env and DB volumes to start fresh..."
	@rm -f .env
	-@docker volume rm $$(docker volume ls -q | grep -E '^bones_bones-db-data$$') 2>/dev/null || true
	@echo "✅ Reset complete. Run 'make init' to create a new .env. Add API and 'make up'"
