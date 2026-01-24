# TaskTimer

[![CI](https://github.com/jeffhoek/tasktimer/actions/workflows/ci.yml/badge.svg)](https://github.com/jeffhoek/tasktimer/actions/workflows/ci.yml)

A FastAPI application for tracking time spent on tasks.

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

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your DATABASE_URL
```

4. Run the application:
```bash
./run.sh
# or
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
