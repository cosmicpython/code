build:
	docker-compose build

api:
	docker-compose up -d app

test:
	pytest --tb=short

all: build api test
