from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ProductOut(BaseModel):
    id: UUID
    name: str
    category: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True
