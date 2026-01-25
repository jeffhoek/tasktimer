# TaskTimer

[![CI](https://github.com/jeffhoek/tasktimer/actions/workflows/ci.yml/badge.svg)](https://github.com/jeffhoek/tasktimer/actions/workflows/ci.yml)

A FastAPI application for tracking time spent on tasks.

## Requirements

- Python: [uv](https://docs.astral.sh/uv/) is recommended but you can also use pure Python + pip.
- SQL database: [SQLite](https://sqlite.org/) and [Postgres](https://sqlite.org/) have been tested.
- Curl: You will need [curl]https://curl.se/ to run the example API requests below.


## API

### POST /track

Start tracking a new task.

```bash
curl -X POST http://localhost:8000/track -H "Content-Type: application/json" -d '{"user_id": 123, "description": "Working on feature X"}'
```

**Response:** `{"id": 1, "user_id": 123}`

### POST /stop

Stop tracking a task.

```bash
curl -X POST http://localhost:8000/stop -H "Content-Type: application/json" -d '{"id": 1, "user_id": 123}'
```

**Response:** `{"id": 1, "user_id": 123}`

### GET /times

Get tasks for a user on a specific date with calculated time spent.

```bash
curl "http://localhost:8000/times?user_id=123&date=2024-01-15"
```

**Response:** `[{"id": 1, "description": "Working on feature X", "time_spent": 3600.0}]`


## Quickstart

### Setup environment

#### [uv](https://docs.astral.sh/uv/) (recommended)

```bash
uv sync
```

#### pip (alternatively)
> _If you ran the `uv sync` command above then skip these steps._

```bash
python -m venv .venv
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

### 2. Configure secrets
```bash
cp .env.example .env
# Edit .env with your DATABASE_URL
```

### 3. Run the application

#### uv
```bash
uv run uvicorn tasktimer.main:app --reload
```

#### Python venv / pip

```bash
uvicorn tasktimer.main:app --reload
```

The API will be available at http://localhost:8000

## Running Tests

```bash
python -m unittest tests.test_main -v
```

## Code Formatting

This project uses [Black](https://black.readthedocs.io/) for code formatting.

```bash
# Check formatting
black --check .

# Apply formatting
black .
```
