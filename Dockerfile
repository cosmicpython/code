FROM python:3.8-alpine

RUN apk add --no-cache --virtual .build-deps gcc postgresql-dev musl-dev python3-dev \
    && pip install --no-cache-dir mypy psycopg2-binary \
    && apk add libpq \
    && apk del --no-cache .build-deps

COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt 

RUN mkdir -p /src
COPY src/ /src/
RUN pip install -e /src
COPY tests/ /tests/

WORKDIR /src
