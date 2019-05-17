FROM python:3.9-slim-buster

# RUN apt install gcc libpq (no longer needed bc we use psycopg2-binary)

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

RUN mkdir -p /src
COPY src/ /src/
RUN pip install -e /src
COPY tests/ /tests/

WORKDIR /src
ENV DJANGO_SETTINGS_MODULE=djangoproject.django_project.settings
CMD python /tests/wait_for_postgres.py && \
    python /src/djangoproject/manage.py migrate && \
    python /src/djangoproject/manage.py runserver 0.0.0.0:80
