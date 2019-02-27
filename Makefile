build:
	docker-compose build

api:
	docker-compose up -d app

test:
	docker-compose run --rm --entrypoint='pytest /tests' app

unit-tests:
	docker-compose run --rm --entrypoint='pytest /tests/unit' app

integration-tests:
	docker-compose run --rm --entrypoint='pytest /tests/integration' app

e2e-tests:
	docker-compose run --rm --entrypoint='pytest /tests/e2e' app

logs:
	docker-compose logs app | tail -100

down:
	docker-compose down --remove-orphans

all: down build api test
