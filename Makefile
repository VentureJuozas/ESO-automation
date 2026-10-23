PYTHON ?= python3
export PYTHONPATH := src:.
export ESO_STEP_DELAY ?= 0.11

.PHONY: install demo test web web-build docker

docker:
	docker compose up --build

install:
	$(PYTHON) -m pip install -r requirements.txt

web:
	cd web && npm install

web-build: web
	cd web && npm run build

demo: install web-build
	$(PYTHON) -m uvicorn app.main:app --host 0.0.0.0 --port 8000

test: install
	ESO_STEP_DELAY=0 $(PYTHON) -m pytest -q

e2e: web-build
	cd web && npx playwright test
