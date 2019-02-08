test:
	pytest --tb=short

watch-tests:
	ls *.py | entr pytest --tb=short

black:
	black -l 86 $$(find * -name '*.py')
