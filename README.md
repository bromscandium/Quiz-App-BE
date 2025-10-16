# Quiz App Backend

This is the **Python** backend for Quiz App, implemented with **FastAPI**, **PostgreSQL**, **Redis**, and **Docker**.

---

## Project Structure

```
Quiz-App-BE/
├── app/
│ ├── core/                         # Core settings and configurations for the app
│ │ ├── __init__.py 
│ │ ├── app.py 
│ │ ├── base.py 
│ │ └── security.py 
│ ├── db/                           # Modules for database interactions
│ │ ├── __init__.py 
│ │ ├── postgres.py
│ │ └── redis.py
│ ├── dependencies/                 # Dependencies for backend
│ │ ├── __init__.py 
│ │ └── auth0_dependency.py 
│ ├── exceptions/                   # Custom exceptions
│ │ ├── __init__.py 
│ │ ├── auth_exceptions.py
│ │ ├── health_check.py 
│ │ ├── refresh_token_exceptions.py
│ │ └── user_exceptions.py 
│ ├── models/                       # Models (for instance, User or QuizCard) for managing objects in application
│ │ ├── __init__.py 
│ │ ├── base.py
│ │ ├── mixins.py 
│ │ ├── refresh_token_model.py
│ │ └── user_model.py     
│ ├── repositories/                 # Repositories for database access and data operations
│ │ ├── __init__.py 
│ │ ├── base_repository.py 
│ │ ├── refresh_token_repository.py
│ │ └── user_repository.py    
│ ├── routers/                      # Routers for application
│ │ ├── __init__.py 
│ │ ├── auth_router.py     
│ │ ├── health_check.py         
│ │ └── user_router.py     
│ ├── schemas/                      # Pydantic schemas for data validation
│ │ ├── __init__.py 
│ │ ├── auth_schema.py
│ │ ├── health_check.py 
│ │ └── user_schema.py 
│ ├── services/                     # Business logic and services
│ │ ├── __init__.py 
│ │ ├── auth_service.py
│ │ ├── refresh_token_service.py
│ │ └── user_service.py 
│ ├── unit_of_work/                 # Unit of work
│ │ ├── __init__.py 
│ │ └── uow.py 
│ ├── utils/                        # Helper functions and utilities
│ │ ├── __init__.py 
│ │ ├── access_token_util.py
│ │ ├── auth0_util.py
│ │ ├── logger.py 
│ │ ├── password_util.py
│ │ └── password_service.py 
│ ├── __init__.py 
│ └── main.py                       # Entry point
├── logs/                           # Logs of your applicaion
├── migrations/                     # Alembic migrations for database
├── secrets/                        # Public and private keys for RSA
├── tests/
│ ├── routers/                      # Router tests
│ │ ├── __init__.py 
│ │ ├── test_auth_router.py  
│ │ ├── test_health_check.py  
│ │ └── test_user_router.py
│ ├── services/                     # Unit tests
│ │ ├── __init__.py 
│ │ └── test_auth_service.py 
│ │ └── test_refresh_token_service.py
│ │ └── test_user_service.py  
│ ├── __init__.py 
│ ├── conftest.py 
│ ├── factories.py 
│ └── pytest.ini                    # Initial setup for tests
├── .dockerignore 
├── .env.sample                     # Example environment variables, without secrets
├── .gitignore 
├── .pre-commit-config.yaml         # Configuration for pre-commit hooks
├── alembic.ini                 
├── docker-compose.yml              # Docker Compose orchestration
├── Dockerfile                      # Dockerfile for building the app container 
├── poetry.lock 
├── pyproject.toml                  # Project configuration for Poetry 
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

## Database Migrations (Alembic)

This project uses **Alembic** to handle database migrations for PostgreSQL.

### Creating a New Migration

1. Make sure the Docker containers are running:

```bash
docker-compose up -d
```

2. Create a new migration based on changes in your SQLModel or SQLAlchemy models:

```bash
docker-compose exec app alembic revision --autogenerate -m "<migration_name>"
```

This will generate a new migration file in the `migrations/versions/` directory.

### Applying Migrations

1. Apply all pending migrations to the database:

```bash
docker-compose exec app alembic upgrade head
```

2. Verify the applied migrations:

```bash
docker-compose exec postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}
```

Then run in the psql shell (in my case):

```
\dt
```

You should see the `alembic_version` table along with other migrated tables.

### Notes

* Keep all migration scripts in `migrations/versions/` under version control.

---

## Testing

**Run Tests:**

```bash
docker-compose exec app poetry run pytest
```

---

## Health Check Endpoints

The application includes health check endpoints to monitor service status:

* `GET /` - Basic application health check
* `GET /db` - PostgreSQL database connectivity check
* `GET /redis` - Redis connectivity check

---