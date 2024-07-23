PROJECT = vegeta_ss
VENV_NAME = venv

env:
	python3 -m venv venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install -r requirements.txt
	venv/bin/pip install pre-commit
	venv/bin/pre-commit install
