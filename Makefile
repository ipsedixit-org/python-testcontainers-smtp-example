setup:
	python3 -m venv .venv ; \
	. .venv/bin/activate ; \
	pip install -r requirements.txt ;\
	pip install -r requirements_test.txt

test:
	pytest --log-cli-level DEBUG --capture=tee-sys --cov=python_testcontainers_smtp_example tests tests_integration

lint:
	black python_testcontainers_smtp_example tests tests_integration
	isort python_testcontainers_smtp_example tests tests_integration

pep8:
	flake8 python_testcontainers_smtp_example tests tests_integration

tox:
	tox -e tests,pep8
