install:
	pipenv install --dev

package_vulnerability:
	PIPENV_PYUP_API_KEY="" pipenv check

flake:
	pipenv run flake8 .

lint: flake

check: package_vulnerability flake

test: package_vulnerability flake at_tests

at_tests:
	pipenv run python run.py --log_level WARN