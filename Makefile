build:
	docker-compose build

api:
	docker-compose up -d app

test:
	pytest --tb=short

logs:
	docker-compose logs app | tail -100

all: build api test
