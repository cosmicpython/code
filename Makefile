build:
	docker-compose build

services:
	docker-compose up -d

test:
	docker-compose run --rm --entrypoint='pytest /tests' api

unit-tests:
	docker-compose run --rm --entrypoint='pytest /tests/unit' api

integration-tests:
	docker-compose run --rm --entrypoint='pytest /tests/integration' api

e2e-tests:
	docker-compose run --rm --entrypoint='pytest /tests/e2e' api

logs:
	docker-compose logs --tail=25 api redis_pubsub

down:
	docker-compose down --remove-orphans

all: down build services test
