PIP=pip
RUN_TESTS=py.test --cov=tests --cov nicedjango --cov-report=term-missing --cov-report html

dev_env:
	$(PIP) install -r requirements/devel.txt
	
test:
	$(RUN_TESTS)
	
test_verbose:
	$(RUN_TESTS) --capture=no
	
coverage: dev_env
	tox -e coverage
	coverage html
	xdg-open htmlcov/index.html
	
style:
	@echo "Autopep8..."
	autopep8 --aggressive --max-line-length 100 --in-place --ignore E309,E501,E128 -r nicedjango tests
	@echo "Formatting python imports..."
	isort -l 100 -rc nicedjango/ tests/
	@echo "Pyflakes..."
	find tests -name "[a-z]*.py" -exec pyflakes {} \;
	find nicedjango -name "[a-z]*.py" -exec pyflakes {} \;
	
clean:
	-find . -name __pycache__ -type d | xargs rm -rf
	-find . -name "*.pyc"| xargs rm -f
	-rm -rf dist/ build/ src/*.egg-info
	
bumpversion:
	bumpversion part --new-version $(VERSION)
	
publish_release:
	python setup.py sdist --formats=bztar,zip,gztar upload
	python setup.py bdist_wheel upload
