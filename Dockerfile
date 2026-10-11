FROM python:3.13

WORKDIR /app

COPY . /app

COPY pyproject.toml poetry.lock* /app/
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi \
    && pip install alembic sqlmodel pytest

CMD ["poetry", "run", "start"]
