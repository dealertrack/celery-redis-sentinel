.PHONY: clean-pyc clean-build docs clean

COVER_CONFIG_FLAGS=--with-coverage --cover-package=celery_redis_sentinel,tests --cover-tests
COVER_REPORT_FLAGS=--cover-html --cover-html-dir=htmlcov
COVER_FLAGS=${COVER_CONFIG_FLAGS} ${COVER_REPORT_FLAGS}

help:
	@echo "install - install all requirements including for testing"
	@echo "clean - remove all artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "clean-test-all - remove all test-related artifacts including tox"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "test-coverage - run tests with coverage report"
	@echo "test-all - run tests on every Python version with tox"
	@echo "check - run all necessary steps to check validity of project"
	@echo "release - package and upload a release"
	@echo "dist - package"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "livedocs - generate Sphinx HTML documentation and start auto-restart docs server"

install:
	pip install -r requirements-dev.txt

install-quiet:
	pip install -r requirements-dev.txt > /dev/null

clean: clean-build clean-pyc clean-test-all

clean-build:
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info

clean-pyc:
	@find . -name '*.pyc' -follow -print0 | xargs -0 rm -f
	@find . -name '*.pyo' -follow -print0 | xargs -0 rm -f
	@find . -name '__pycache__' -type d -follow -print0 | xargs -0 rm -rf

clean-test:
	rm -rf .coverage coverage*
	rm -rf htmlcov/

clean-test-all: clean-test
	rm -rf .tox/

lint:
	flake8 celery_redis_sentinel tests

test:
	py.test -v --cov=celery_redis_sentinel --cov-report=term-missing tests/

test-all:
	tox

check: clean-build clean-pyc clean-test lint test

release: clean
	python setup.py sdist upload

dist: clean
	python setup.py sdist
	ls -l dist

docs:
	cd docs && make html && open _build/html/index.html

livedocs:
	cd docs && make livehtml

