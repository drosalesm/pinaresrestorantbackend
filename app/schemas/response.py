from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel

T = TypeVar("T")

class ResponseModel(BaseModel, Generic[T]):
    message: str
    status: bool
    http_code: int
    data: Optional[List[T]] = None


