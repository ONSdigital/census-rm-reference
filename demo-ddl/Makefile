install:
	pipenv install --dev

check:
	PIPENV_PYUP_API_KEY="" pipenv check

lint:
	pipenv run flake8

test: check lint
	pipenv run pytest