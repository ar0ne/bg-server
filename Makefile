py_warn = PYTHONDEVMODE=1


test_server:
	$(py_warn) py.test server/

test_client:
	cd client/ && npm test -- --watchAll=false

test: test_server test_client
