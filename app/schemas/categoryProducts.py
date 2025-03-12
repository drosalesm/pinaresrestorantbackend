from pydantic import BaseModel
from typing import Optional

class CategoryProductCreate(BaseModel):
    name: str
    

class CategoryProductUpdate(BaseModel):
    name: str | None = None


class CategoryProductResponse(BaseModel):
    status_code: int
    message: str
    data: Optional[dict] = None