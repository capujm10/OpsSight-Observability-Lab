.PHONY: up down restart logs ps test ai-test smoke load errors latency dependency alerts ai-rca alert-webhook postmortems k6-smoke k6-spike k6-sustained clean

up:
	docker compose up -d --build

down:
	docker compose down

restart:
	docker compose down && docker compose up -d --build

logs:
	docker compose logs -f --tail=100

ps:
	docker compose ps

test:
	cd apps/api && pytest
	cd apps/ai-rca && pytest
	pytest tests

ai-test:
	cd apps/ai-rca && pytest

smoke:
	bash scripts/smoke-test.sh

load:
	bash scripts/generate-load.sh

errors:
	bash scripts/simulate-errors.sh

latency:
	bash scripts/simulate-latency.sh

dependency:
	curl -sS http://localhost:8000/api/v1/simulate/dependency-failure | jq .

alerts:
	curl -sS http://localhost:9090/api/v1/alerts | jq .

ai-rca:
	python scripts/sample-ai-rca.py

alert-webhook:
	python scripts/send-alertmanager-webhook.py

postmortems:
	python scripts/generate-postmortem.py

k6-smoke:
	docker compose --profile load run --rm k6 run /scripts/smoke.js

k6-spike:
	docker compose --profile load run --rm k6 run /scripts/spike.js

k6-sustained:
	docker compose --profile load run --rm k6 run /scripts/sustained.js

clean:
	docker compose down -v --remove-orphans
