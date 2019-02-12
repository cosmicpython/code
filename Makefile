test:
	pytest --tb=short -vv

watch-tests:
	ls *.py | entr pytest --tb=short -vv
