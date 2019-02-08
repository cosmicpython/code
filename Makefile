test:
	pytest --tb=short

watch-tests:
	ls *.py | entr pytest --tb=short
