py_warn = PYTHONDEVMODE=1
PY?=python3
REQUIREMENTS_TXT=backend/requirements.txt backend/dev_requirements.txt

.PHONY: test_backend
test_backend: venv
	$(VENV)/py.test backend/

.PHONY: test_frontend
test_frontend:
	cd frontend/ && npm test -- --watchAll=false

.PHONY: test
test: test_backend test_frontend


include Makefile.venv
