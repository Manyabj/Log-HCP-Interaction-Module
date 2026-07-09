from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class HCPOut(BaseModel):
    id: UUID
    name: str
    specialty: Optional[str] = None
    hospital: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    class Config:
        from_attributes = True
