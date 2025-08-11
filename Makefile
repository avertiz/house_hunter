VENV_DIR := .venv
PYTHON := /home/avertiz/repos/skyscanner/Python-3.12.8/python

.PHONY: help setup run clean

help:
	@echo "Usage:"
	@echo "  make setup   - Set up virtual environment and install dependencies"
	@echo "  make run     - Run the Flask app"
	@echo "  make clean   - Remove virtual environment"

setup:
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install --upgrade pip
	$(VENV_DIR)/bin/pip install -r requirements.txt

run:
	FLASK_APP=app.py FLASK_ENV=development $(VENV_DIR)/bin/flask run --host=0.0.0.0 --port=8080

clean:
	rm -rf $(VENV_DIR)

migrate:
	$(VENV_DIR)/bin/flask db migrate
	$(VENV_DIR)/bin/flask db upgrade
