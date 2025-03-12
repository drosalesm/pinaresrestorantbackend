from pydantic import BaseModel
from datetime import datetime

class LogEntrySchema(BaseModel):
    timestamp: datetime
    endpoint: str
    method: str
    status_code: int
    message: str | None = None

    class Config:
        orm_mode = True
