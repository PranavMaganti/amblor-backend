FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

ENV MODULE_NAME="server.app"

COPY ./ /app

RUN pip install poetry

RUN poetry config virtualenvs.create false

RUN poetry install