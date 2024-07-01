test:
	pytest --tb=short

watch-tests:
	ls *.py | entr pytest --tb=short

black:
	black -l 86 $$(find * -name '*.py')

db-up:
	docker run --name some-postgres -e POSTGRES_PASSWORD=mysecretpassword -p 5555:5432 -d postgres

run:
	flask --app flask_app run --debug