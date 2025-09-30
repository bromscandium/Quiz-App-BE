# Quiz App Backend

This is the backend for Quiz App, implemented with **FastAPI** and **Docker**.

---

## Project Structure

```
Quiz-App-BE/
├── app/
│ ├── core/                     # Core settings and configurations for the app
│ │ ├── __init__.py 
│ │ └── config.py 
│ ├── db/                       # Modules for database interactions
│ │ └── __init__.py 
│ ├── schemas/                  # Pydantic schemas for data validation
│ │ ├── __init__.py 
│ │ └── health_check.py 
│ ├── services/                 # Business logic and services
│ │ └── __init__.py 
│ ├── utils/                    # Helper functions and utilities
│ │ └── __init__.py 
│ ├── __init__.py 
│ └── main.py                   # Entry point
├── tests/
│ ├── e2e/                      # End-to-end tests
│ │ └── __init__.py 
│ ├── integration/              # Integration tests
│ │ └── __init__.py 
│ ├── unit/                     # Unit tests
│ │ ├── __init__.py 
│ │ └── test_health_check.py  
│ ├── __init__.py 
│ └── pytest.ini                # Initial setup for tests
├── .dockerignore 
├── .env.sample                 # Example environment variables, without secrets
├── .gitignore 
├── .pre-commit-config.yaml     # Configuration for pre-commit hooks
├── Dockerfile                  # Dockerfile for building the app container 
├── poetry.lock 
├── pyproject.toml              # Project configuration for Poetry 
└── README.md 
```

## Installation and Running with Docker

1. Clone the repository:

```bash
git clone <https://github.com/bromscandium/Quiz-App-BE>
cd Quiz-App-BE
```

2. Build the Docker image:

```bash
docker build -t quiz-app-be .
```

3. Run the Docker container:

```bash
docker run --env-file .env -p 8000:8000 --name quiz-app-be-container quiz-app-be
```

* `--env-file .env` loads environment variables from your `.env` file.
* `-p 8000:8000` maps port 8000 of your local machine to port 8000 of the container.
* `--name quiz-app-be-container` gives your container a name.
* `quiz-app-be` is the name of the Docker image you built.

4. Access the FastAPI server at `http://127.0.0.1:8000`
5. API documentation is available at `http://127.0.0.1:8000/docs`

---

## Stopping and Restarting the Container

* Stop the container:

```bash
docker stop quiz-app-be-container
```

* Restart the container:

```bash
docker start quiz-app-be-container
```

* Check running containers:

```bash
docker ps
```

* Remove the container if needed:

```bash
docker rm quiz-app-be-container
```

---

## Testing

* To run unit tests, use:

```bash
poetry run pytest
```

* Tests are located in the `tests/` folder.
* Pytest will automatically find all `test_*.py` files.

---