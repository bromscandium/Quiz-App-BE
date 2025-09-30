# Quiz App Backend

This is the backend for Quiz App, implemented with **FastAPI**.

---

## Installation and Running

1. Clone the repository:

```bash
git clone <https://github.com/bromscandium/Quiz-App-BE>
cd Quiz-App-BE
```

2. Install dependencies using Poetry:

```bash
poetry install
```

3. Run the FastAPI server:

```bash
poetry run start
```

* The server will run at `http://127.0.0.1:8000`
* UI documentation: `http://127.0.0.1:8000/docs`

---

## Testing

* To run unit tests, use:

```bash
poetry run pytest
```

* Tests are located in the `tests/` folder.
* Pytest will automatically find all `test_*.py` files.

---

## Project Structure

```
Quiz-App-BE/
├── app/
│ ├── core/             # Core settings and configurations for the app
│ │ ├── __init__.py 
│ ├── db/               # Modules for database interactions
│ │ ├── __init__.py 
│ ├── schemas/          # Pydantic schemas for data validation
│ │ ├── __init__.py 
│ ├── services/         # Business logic and services
│ │ ├── __init__.py 
│ ├── utils/            # Helper functions and utilities
│ │ ├── __init__.py 
│ ├── __init__.py 
│ └── main.py           # Entry point
├── tests/
│ ├── test_health_check.py # Unit test for the `/` endpoint
├── .env.sample # Example environment variables, without secrets
├── .gitignore 
├── .pre-commit-config.yaml # Configuration for pre-commit hooks
├── poetry.lock 
├── pyproject.toml # Project configuration for Poetry 
└── README.md 
```

---