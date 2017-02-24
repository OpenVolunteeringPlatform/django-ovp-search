test:
	@python ovp_search/tests/runtests.py

lint:
	@pylint ovp_search

clean-pycache:
	@rm -r **/__pycache__

clean: clean-pycache

.PHONY: clean


