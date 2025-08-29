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