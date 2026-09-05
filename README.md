# HTTP CRUD API

A small learning project that implements an HTTP CRUD API for users with JSON
request and response bodies.

## Features

- Create, read, update, and delete users.
- UUID-based user identification.
- Email validation and uniqueness checks.
- JSON responses and structured JSONL logging.
- Environment-based configuration.
- Unit, integration, and end-to-end tests.
- Docker and Docker Compose support.

## Architecture

The project intentionally does not use a database. User data is stored in a
JSON file, which keeps the project focused on Python, HTTP, validation, and
repository/service interactions.

This is also an intentionally simplified architecture. Application logic is not
split into separate use-case classes, and SRP is not followed everywhere. These
are conscious trade-offs for this learning project, not accidental omissions.

## Requirements

- Python 3.14+
- `uv` (for local development)
- Docker (optional)

## Configuration

Copy `.env.example` to `.env` and adjust the values if needed:

```text
HTTP_HOST=0.0.0.0
HTTP_PORT=8080
DATA_DIR=data
LOG_LEVEL=DEBUG
LOG_DIR=logs
```

`DATA_DIR` and `LOG_DIR` specify directories only; the application manages the
filenames inside them.

The same `DATA_DIR` and `LOG_DIR` values are also used by Docker Compose to
configure bind mounts.

## Run locally

```bash
uv sync
uv run http-crud-api
```

The API is available at `http://localhost:8080`.

## Run with Docker Compose

Create the local environment file from the provided template:

```bash
cp .env.example .env
```

The `.env` file is required by Docker Compose and is not committed to the
repository.

```bash
docker compose up --build
```

The Compose file mounts local `data` and `logs` directories into the
container. These bind mounts keep application data outside the container
filesystem, so users and logs survive container recreation.

## API endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/health` | Health check |
| GET | `/users` | Get all users |
| POST | `/users` | Create a user |
| GET | `/users/{id}` | Get one user |
| PUT | `/users/{id}` | Update a user |
| DELETE | `/users/{id}` | Delete a user |

Example request:

```bash
curl -X POST http://localhost:8080/users \
  -H "Content-Type: application/json" \
  -d '{"name":"John","email":"john@example.com"}'
```

Example response:

```json
{
  "id": "9d4c0000-0000-7000-8000-000000000000",
  "name": "John",
  "email": "john@example.com"
}
```

## Tests

```bash
uv run pytest
```

The test suite contains unit, integration, and end-to-end tests. End-to-end
tests use `.env.test` and run the server as a separate local process.
