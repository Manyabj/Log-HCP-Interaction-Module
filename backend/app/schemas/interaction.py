from typing import List, Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


class InteractionBase(BaseModel):
    hcp_name: Optional[str] = None
    interaction_type: Optional[str] = None
    interaction_date: Optional[str] = None
    interaction_time: Optional[str] = None
    attendees: Optional[List[str]] = Field(default_factory=list)
    topics: Optional[List[str]] = Field(default_factory=list)
    product: Optional[str] = None
    sentiment: Optional[str] = None
    materials: Optional[List[str]] = Field(default_factory=list)
    notes: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[str] = "draft"


class InteractionCreate(InteractionBase):
    session_id: Optional[str] = None


class InteractionUpdate(InteractionBase):
    """All fields optional — only supplied fields are patched."""
    pass


class InteractionOut(InteractionBase):
    id: UUID
    session_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Mandatory fields required before an interaction can be saved / validated.
MANDATORY_FIELDS = ["hcp_name", "interaction_date", "product", "sentiment"]
