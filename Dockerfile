# Source: https://bmaingret.github.io/blog/2021-11-15-Docker-and-Poetry
ARG APP_NAME=jobsity_challenge
ARG APP_PATH=/app/$APP_NAME
ARG POETRY_VERSION=1.1.13
ARG BUILD_PYTHON_VERSION=3.8
ARG FINAL_PYTHON_VERSION=3.8-slim

# Base image to install poetry and copy files
FROM python:$BUILD_PYTHON_VERSION as base
ARG APP_NAME
ARG APP_PATH
ARG POETRY_VERSION
ARG PYTHON_VERSION

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1

ENV POETRY_VERSION=$POETRY_VERSION \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python
ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR $APP_PATH
COPY ./poetry.lock* ./pyproject.toml ./
COPY ./$APP_NAME ./$APP_NAME

# Build stage to export requirements and build the module
FROM base as build
ARG APP_PATH

WORKDIR $APP_PATH
RUN poetry export --format requirements.txt --output requirements.txt --without-hashes
RUN poetry build --format wheel

# Final stage that install the module and its requirements
FROM python:$FINAL_PYTHON_VERSION
ARG APP_NAME
ARG APP_PATH

RUN useradd --create-home appuser
USER appuser
ENV PATH="/home/appuser/.local/bin:$PATH"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1

ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR $APP_PATH
COPY --from=build $APP_PATH/* ./
RUN pip install --upgrade pip
RUN pip install ./$APP_NAME*.whl --constraint requirements.txt

# Debug
# ENTRYPOINT [ "/bin/bash" ]
