from sqlalchemy.orm import Session
from app.models.log import LogEntry
from app.schemas.log import LogEntrySchema

def create_log_entry(db: Session, endpoint: str, method: str, status_code: int, message: str = None):
    log_entry = LogEntry(
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        message=message
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry
