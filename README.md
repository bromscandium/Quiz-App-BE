# Quiz App Backend

This is the **Python** backend for Quiz App, implemented with **FastAPI**, **PostgreSQL**, **Redis**, and **Docker**.

---

## Project Structure

```
Quiz-App-BE/
├── app/
│ ├── core/                     # Core settings and configurations for the app
│ │ ├── __init__.py 
│ │ └── config.py 
│ ├── db/                       # Modules for database interactions
│ │ ├── __init__.py 
│ │ ├── postgres.py
│ │ └── redis.py
│ ├── models/                   # Models (for instance, User or QuizCard) for managing objects in application
│ │ └── __init__.py     
│ ├── routers/                  # Routers for application
│ │ ├── __init__.py 
│ │ └── health_check.py         
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
│ ├── conftest.py 
│ └── pytest.ini                # Initial setup for tests
├── .dockerignore 
├── .env.sample                 # Example environment variables, without secrets
├── .gitignore 
├── .pre-commit-config.yaml     # Configuration for pre-commit hooks
├── docker-compose.yml          # Docker Compose orchestration
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

2. Build and run the Docker:

```bash
docker-compose up
```

3. Rebuild After Code Changes:

```bash
docker-compose up --build
```

4. Stop Services:

```bash
docker-compose down
```

5. Stop and Remove Volumes (Deletes Database Data)

```bash
docker-compose down -v
```

---

## Accessing the Application

* API Server: http://{YOUR_LINK}:{YOUR_PORT}
* API Documentation (Swagger): http://{YOUR_LINK}:{YOUR_PORT}/docs

---

## Testing

### Prerequisites

Activate virtual environment (if running locally):

**Windows:**

```bash
venv\Scripts\activate
```

**Linux/Mac:**

```bash
source venv/bin/activate
```

**Run Tests:**

```bash
poetry run pytest
```

---

## Health Check Endpoints

The application includes health check endpoints to monitor service status:

* `GET /` - Basic application health check
* `GET /db` - PostgreSQL database connectivity check
* `GET /redis` - Redis connectivity check

---