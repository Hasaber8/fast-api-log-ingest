import asyncio
from typing import Union, List, Optional
from fastapi import FastAPI, Query
from pydantic import BaseModel
from datetime import date, datetime, timedelta
import uuid

app = FastAPI()

# model for log entries
class LogEntry(BaseModel):
    id: str = ""
    service_name: str
    timestamp: datetime = None
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "service_name": "auth-service",
                "timestamp": "2025-03-17T10:15:00Z",
                "message": "User login successful"
            }
        }

# logs are in-memory for now
logs_db = []

# cleanup interval in seconds
CLEANUP_INTERVAL = 3600 # cleanup every hour
LOG_EXPIRATION_TIME = timedelta(hours=1)

async def cleanup_expired_logs():
    # bacground task to remove logs older than expiration
    while True:
        try:
            global logs_db
            current_time = datetime.utcnow()
            expiration_threshold = current_time - LOG_EXPIRATION_TIME

            log_count_before = len(logs_db)

            # remove expired logs
            logs_db = [log for log in logs_db if log["timestamp"] > expiration_threshold]

            deleted_count = log_count_before - len(logs_db)

            if deleted_count > 0:
                print(f"Removed {deleted_count} expired logs")
            else:
                print(f"No expired logs found")
            
            await asyncio.sleep(CLEANUP_INTERVAL)
        except Exception as e :
            print(f"Error in cleanup task: {str(e)}")
            await asyncio.sleep(CLEANUP_INTERVAL)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(cleanup_expired_logs())
    print("Background cleanup task started.")

@app.get("/")
def read_root():
    return {"Hello": "Sonatus"}

@app.post("/log", status_code=201)
def ingest_log(log_entry: LogEntry):
    # assign uuid4
    if not log_entry.id:
        log_entry.id = str(uuid.uuid4())
    
    # assign timestamp if not provided
    if not log_entry.timestamp:
        log_entry.timestamp = datetime.utcnow()
    
    log_dict = log_entry.dict()
    logs_db.append(log_dict)

    return {"id": log_entry.id, "message": "Log entry created successfully"}

@app.get("/log", response_model=List[LogEntry])
def get_logs(
    service_name: Optional[str] = None,
    start: Optional[datetime] = Query(None, description="Start time in ISO format (YYYY-MM-DDTHH:MM:SS)"),
    end: Optional[datetime] = Query(None, description="End time in ISO format (YYYY-MM-DDTHH:MM:SS)")
):
    filtered_logs = logs_db.copy()
    
    # filter by service name if provided
    if service_name:
        filtered_logs = [log for log in filtered_logs if log["service_name"] == service_name]
    
    # filter by start time if provided - handle timezone-aware vs naive comparison
    if start:
        # make sure both datetimes are either naive or aware for comparison
        if start.tzinfo is not None:
            # ff start has timezone info but stored timestamps don't, make start naive
            start = start.replace(tzinfo=None)
        filtered_logs = [log for log in filtered_logs if log["timestamp"] >= start]
    
    # filter by end time if provided - handle timezone-aware vs naive comparison
    if end:
        # make sure both datetimes are either naive or aware for comparison
        if end.tzinfo is not None:
            # if end has timezone info but stored timestamps don't, make end naive
            end = end.replace(tzinfo=None)
        filtered_logs = [log for log in filtered_logs if log["timestamp"] <= end]
    
    # Sort logs by timestamp (oldest first)
    filtered_logs.sort(key=lambda x: x["timestamp"])
    
    return filtered_logs
