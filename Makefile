.PHONY: clean-pyc clean-build docs

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "config - install package and its production dependencies"
	@echo "config-test - install package and its test dependencies"
	@echo "config-develop - install package and its development dependencies"
	@echo "coverage - run coverage test"
	@echo "test - run tests"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release"
	@echo "sdist - package"

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

config:
	pip install .

config-test:
	pip install -e .[test]

config-develop:
	pip install -e .[develop]

test: clean
	coverage run --source pancake -m py.test -l
	@coverage report

coverage: test
	@coverage html
	@echo "open htmlcov/index.html"

docs:
	rm -f docs/pancake.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ pancake
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	@echo "open docs/_build/html/index.html"

release: clean docs test
	python setup.py sdist upload

sdist: clean docs test
	python setup.py sdist
	@ls -l dist