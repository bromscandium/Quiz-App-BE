# Quiz App Backend

This is the **Python** backend for Quiz App, implemented with **FastAPI**, **PostgreSQL**, **Redis**, and **Docker**.

---

## Project Structure

```
Quiz-App-BE/
├── app/
│ ├── core/                         # Core settings and configurations for the app
│ ├── db/                           # Modules for database interactions
│ ├── dependencies/                 # Dependencies for backend
│ ├── enums/                        # Enumerators for using in DB or services
│ ├── exceptions/                   # Custom exceptions
│ ├── models/                       # Models (for instance, User or QuizCard) for managing objects in application
│ ├── persmissions/                 # Special permissions of checking availability to use function further
│ ├── repositories/                 # Repositories for database access and data operations
│ ├── routers/                      # Routers for application
│ ├── schemas/                      # Pydantic schemas for data validation
│ ├── services/                     # Business logic and services
│ ├── tasks/                        # Tasks for celery
│ ├── unit_of_work/                 # Unit of work
│ ├── utils/                        # Helper functions and utilities
│ ├── __init__.py 
│ └── main.py                       # Entry point
├── logs/                           # Logs of your applicaion
├── migrations/                     # Alembic migrations for database
├── secrets/                        # Public and private keys for RSA
├── tests/
│ ├── services/                     # Services tests
│ ├── __init__.py 
│ ├── conftest.py 
│ └── pytest.ini                    # Initial setup for tests
├── .dockerignore 
├── .env.sample                     # Example environment variables, without secrets
├── .env.test                       # enviroment for test database
├── .gitignore 
├── .pre-commit-config.yaml         # Configuration for pre-commit hooks
├── alembic.ini                 
├── docker-compose.yml              # Docker Compose orchestration
├── Dockerfile                      # Dockerfile for building the app container 
├── poetry.lock 
├── pyproject.toml                  # Project configuration for Poetry 
├── alembic.ini  
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
docker-compose up --build
```

3. Rebuild After Code Changes:

```bash
docker-compose up 
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
docker-compose exec app pytest
```

---

## Health Check Endpoints

The application includes health check endpoints to monitor service status:

* `GET /` - Basic application health check
* `GET /db` - PostgreSQL database connectivity check
* `GET /redis` - Redis connectivity check

---