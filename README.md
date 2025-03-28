# FastAPI Log Ingestion System

- Written for Sonatus's technical assesment.

## Requirements

- Python 3.8+
- FastAPI
- Uvicorn (ASGI server)
- Pydantic
- aiohttp (for load testing)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Start the FastAPI server:
```bash
uvicorn main:app --reload
```

The server will start at `http://127.0.0.1:8000`.

## API Endpoints

### POST /log
Submits a new log entry.

Example request:
```bash
curl -X POST http://localhost:8000/log -H "Content-Type: application/json" \
  -d '{"service_name": "auth-service", "message": "User login successful"}'
```

### GET /log
Retrieves logs with optional filtering.

Parameters:
- `service_name`: Filter by service name
- `start`: Filter logs with timestamp greater than or equal to this time
- `end`: Filter logs with timestamp less than or equal to this time

Example requests:
```bash
# Get all logs
curl http://localhost:8000/log

# Filter by service name
curl http://localhost:8000/log?service_name=auth-service

# Filter by time range
curl "http://localhost:8000/log?service_name=auth-service&start=2025-03-27T00:00:00Z&end=2025-03-27T23:59:59Z"
```

