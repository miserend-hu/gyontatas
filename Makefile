.PHONY: start dev stop restart lint seed purge migrate upgrade simulate simulate_local

start:
	docker compose up

dev:
	docker compose up --build

stop:
	docker compose down

restart: stop start

migrate:
	docker compose exec managementtool python manage.py migrate

upgrade: stop
	git pull
	docker compose up --build -d
	$(MAKE) migrate

lint:
	cd apps/managementtool && uv run ruff check . && uv run ruff format --check .

seed:
	docker compose exec managementtool python manage.py seed

purge:
	docker compose down -v

simulate:
	docker compose run --rm --build device_simulator python simulator.py $(ARGS)

simulate_local:
	cd apps/device_simulator && \
	{ test -d .venv || python3 -m venv .venv; } && \
	.venv/bin/pip install -q -r requirements.txt && \
	.venv/bin/python simulator.py --host localhost $(ARGS)
