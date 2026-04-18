.PHONY: start dev lint

start:
	docker compose up

dev:
	docker compose up --build

lint:
	cd apps/managementtool && uv run ruff check . && uv run ruff format --check .
