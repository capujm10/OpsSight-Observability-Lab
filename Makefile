.PHONY: up down restart logs ps lint format format-check typecheck test ai-test validate-yaml validate-compose validate-k8s validate-kustomize audit security-audit observability-check synthetic-monitor validate-all capture-demo-assets release-notes ci-local smoke load errors latency dependency dependency-outage degraded-upstream incident-sim alerts ai-rca alert-webhook postmortems k6-smoke k6-spike k6-sustained clean

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

lint:
	python -m ruff check apps scripts tests

format:
	python -m ruff format apps scripts tests

format-check:
	python -m ruff format --check apps scripts tests

typecheck:
	python -m mypy --no-incremental --config-file pyproject.toml apps/api/app
	python -m mypy --no-incremental --config-file pyproject.toml apps/dependency/app
	python -m mypy --no-incremental --config-file pyproject.toml apps/ai-rca/app

test:
	cd apps/api && python -m pytest
	cd apps/ai-rca && python -m pytest
	python -m pytest tests

validate-yaml:
	python -m yamllint -d "{extends: relaxed, rules: {line-length: disable}}" docker-compose.yml observability k8s .github helm

validate-compose:
	docker compose config --quiet

validate-k8s:
	kubectl apply --dry-run=client --validate=false \
		-f k8s/base/namespace.yaml \
		-f k8s/base/configmap.yaml \
		-f k8s/base/secret-placeholder.yaml \
		-f k8s/api/ai-rca-deployment.yaml \
		-f k8s/api/ai-rca-service.yaml \
		-f k8s/api/api-deployment.yaml \
		-f k8s/api/api-service.yaml \
		-f k8s/api/dependency-deployment.yaml \
		-f k8s/api/dependency-service.yaml \
		-f k8s/api/hpa.yaml \
		-f k8s/api/ingress.yaml \
		-f k8s/api/networkpolicy.yaml \
		-f k8s/monitoring/alloy-configmap.yaml \
		-f k8s/monitoring/kube-state-metrics.yaml \
		-f k8s/monitoring/prometheus-pvc.yaml

validate-kustomize:
	bash scripts/validate-kustomize.sh

audit:
	python -m pip_audit -r apps/api/requirements.txt -r apps/dependency/requirements.txt -r apps/ai-rca/requirements.txt -r apps/local-runtime-exporter/requirements.txt

security-audit:
	bash scripts/security-audit.sh

observability-check:
	bash scripts/observability-check.sh

synthetic-monitor:
	bash scripts/synthetic-monitor.sh

validate-all:
	bash scripts/validate-all.sh

capture-demo-assets:
	bash scripts/capture-demo-assets.sh

release-notes:
	bash scripts/generate-release-notes.sh

ci-local: lint format-check typecheck test validate-yaml validate-compose validate-k8s validate-kustomize

ai-test:
	cd apps/ai-rca && python -m pytest

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

dependency-outage:
	bash scripts/simulate-incident.sh dependency-outage

degraded-upstream:
	bash scripts/simulate-incident.sh degraded-upstream

incident-sim:
	bash scripts/simulate-incident.sh all

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
