run: .venv
	.venv/bin/python ldes-static-conversion/run-ldes-static-conversion.py

install-requirements: .venv
	.venv/bin/pip install -r ldes-static-conversion/requirements.txt

freeze-requirements: .venv
	.venv/bin/python3 -m pip freeze > ldes-static-conversion/requirements.txt

.venv:
	python3 -m venv .venv

.PHONY: install-requirements freeze-requirements run
