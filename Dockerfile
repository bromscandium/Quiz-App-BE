FROM python:3.12

WORKDIR /app

COPY README.md /app/
COPY pyproject.toml poetry.lock* /app/
COPY . /app

RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi


EXPOSE 8000

CMD ["poetry", "run", "start"]
