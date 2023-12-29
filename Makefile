py_warn = PYTHONDEVMODE=1
PY?=python3
REQUIREMENTS_TXT=server/requirements.txt server/dev_requirements.txt

.PHONY: test_server
test_server: venv
	$(VENV)/py.test server/

.PHONY: test_client
test_client:
	cd client/ && npm test -- --watchAll=false

.PHONY: test
test: test_server test_client


include Makefile.venv
