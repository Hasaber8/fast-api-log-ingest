from typing import Union, List, Optional
from fastapi import FastAPI, Query
from pydantic import BaseModel
from datetime import datetime
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
def fet_logs(
    service_name: Optional[str] = None,
    start_time: Optional[datetime] = Query(None, description="Start time in ISO format (YYYY-MM-DDTHH:MM:SS)"),
    end_time: Optional[datetime] = Query(None, description="End time in ISO format (YYYY-MM-DDTHH:MM:SS)")
):
    filtered_logs = logs_db.copy()
    
    # filter by service name if provided
    if service_name:
        filtered_logs = [log for log in filtered_logs if log["service_name"] == service_name]
    
    # filter by start time if provided
    if start_time:
        filtered_logs = [log for log in filtered_logs if log["timestamp"] >= start_time]
    
    # filter by end time if provided
    if end_time:
        filtered_logs = [log for log in filtered_logs if log["timestamp"] <= end_time]
    
    return filtered_logs
