PACKAGE=dist/$(shell ls dist | tail -n 1)
USERNAME ?=
PASSWORD ?=

install:
	pipenv sync

install-dev:
	pipenv sync --dev

clean:
	pipenv run python setup.py clean

build: clean
	pipenv run python setup.py sdist

deploy: build
	pipenv run twine upload $(PACKAGE) -u $(USERNAME) -p $(PASSWORD)
