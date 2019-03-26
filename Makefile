build:
	docker-compose build

up:
	docker-compose up -d app

test:
	pytest --tb=short

all: build up test
