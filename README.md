# Postgres - Python Backend Framework

A robust Python backend framework using FastAPI, SQLAlchemy ORM, and PostgreSQL following MVC architecture.

## Features

- **MVC Architecture**: Clean separation of concerns
- **PostgreSQL Integration**: Direct connection to local PostgreSQL database
- **ORM Support**: SQLAlchemy for database operations
- **Migration System**: Alembic for database migrations
- **Middleware Stack**: Logging, error handling, authentication, etc.
- **API Documentation**: Automatic Swagger/OpenAPI documentation
- **Environment Management**: Configuration for different environments
- **Testing Framework**: Pytest setup for unit and integration tests

## Project Structure

```
app/
├── config/         # Configuration files and settings
├── controllers/    # Business logic and request handling
├── middlewares/    # Custom middleware components
├── migrations/     # Database migration scripts
├── models/         # SQLAlchemy ORM models
├── tests/          # Test cases
├── utils/          # Helper functions and utilities
└── views/          # API routes and endpoints
```

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL
- Docker (optional, for containerized PostgreSQL)

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd VibeLogBE
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Start PostgreSQL using Docker:
   ```
   docker compose up -d
   ```

5. Set up environment variables:
   ```
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. Run database migrations:
   ```
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

7. Start the server:
   ```
   uvicorn app.main:app --reload
   ```

## Usage

Access the API documentation at `http://localhost:8000/docs` after starting the server.

## Development

### Creating a New Model

Add a new model in `app/models/` following the SQLAlchemy ORM pattern.

### Adding a New Endpoint

1. Create controller logic in `app/controllers/`
2. Define routes in `app/views/`
3. Register routes in `app/main.py`

### Running Tests

```
pytest
```

## License

[MIT License](LICENSE)
