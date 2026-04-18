.PHONY: start dev lint seed purge simulate

start:
	docker compose up

dev:
	docker compose up --build

lint:
	cd apps/managementtool && uv run ruff check . && uv run ruff format --check .

seed:
	docker compose exec managementtool python manage.py seed

purge:
	docker compose down -v

simulate:
	docker compose run --rm --build device_simulator python simulator.py $(ARGS)
