# TaskTimer

[![CI](https://github.com/jeffhoek/tasktimer/actions/workflows/ci.yml/badge.svg)](https://github.com/jeffhoek/tasktimer/actions/workflows/ci.yml) [![CodeQL Advanced](https://github.com/jeffhoek/tasktimer/actions/workflows/codeql.yml/badge.svg)](https://github.com/jeffhoek/tasktimer/actions/workflows/codeql.yml)

A FastAPI application for tracking time spent on tasks.

## Requirements

- Python: [uv](https://docs.astral.sh/uv/) is recommended but you can also use pure Python + pip.
- SQL database: [SQLite](https://sqlite.org/) and [Postgres](https://sqlite.org/) have been tested.
- Curl: You will need [curl](https://curl.se/) to run the example API requests below.


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


## OpenShift Deployment

Deploy to OpenShift using the [s2i](https://github.com/openshift/source-to-image) builder with the following commands below. (If your OpenShift instance doesn't have the version of Python specified in [.python-version](./.python-version) and [pyproject.toml](./pyproject.toml) then you may need to install the template for the correct python version.)

First, create a new project:
```
oc new-project tasktimer
```

Next, create the `DATABASE_URL` connection string as a secret. (We will set this secret on the deployment after creating the app.) If you're running Postgres on your localhost the connection string might look something like this:
```
oc create secret generic app-secret --from-literal=DATABASE_URL="postgresql://postgresuser:postgrespw@My-MacBook-Pro.local:5432/tasktimer"
```

Next, create the app:
```
oc new-app "https://github.com/jeffhoek/tasktimer.git"
```

After creating the app you will need to set the secret on the deployment. Use this command:
```
oc set env --from=secret/app-secret deploy/tasktimer
```

After the build completes ensure the pod is up running and shows `1/1` in the READY column.
```
oc get pods
```
```
NAME                        READY   STATUS      RESTARTS   AGE
tasktimer-1-build           0/1     Completed   0          14m
tasktimer-7db964699-hbtvx   1/1     Running     0          8m46s
```

Next, create a route in order to test with curl.

Create the route:
```
oc create route edge --service=tasktimer
```

Get the route:
```
oc get route
```
```
NAME        HOST/PORT                                 PATH   SERVICES    PORT       TERMINATION   WILDCARD
tasktimer   tasktimer-tasktimer.apps-crc.testing          tasktimer   8080-tcp   edge          None
```

Now you should be able to use curl to test the API. If you are testing on [OpenShift Local](), then the curl command might look something like this:

```
curl -k -XPOST -H "content-type: application/json" "https://tasktimer-tasktimer.apps-crc.testing/track" -d '{"user_id": 123, "description": "Working on feature X"}'
```

The other curl examples above should also work, but you'll need to update the URL and data payload accordingly.
