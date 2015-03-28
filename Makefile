help:
	@echo 'Usage: '
	@echo '   make clean                       clean the dists directory '
	@echo '   make build                       build the package into a wheel and sdist '
	@echo '   make release-test                push to the Test PyPI '
	@echo '   make release                     push to the PyPI '
	@echo ''


clean:
	rm -rf build dist htmlcov .tox

build: clean
	python setup.py bdist_wheel sdist

release-test: build
	twine upload -r pypitest dist/*

release: build
	twine upload dist/*
