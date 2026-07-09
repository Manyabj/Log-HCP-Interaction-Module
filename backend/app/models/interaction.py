import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class Interaction(Base):
    """A single logged HCP interaction (call, meeting, event, etc.)."""

    __tablename__ = "interaction"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), index=True, nullable=True)

    hcp_id = Column(UUID(as_uuid=True), ForeignKey("hcp.id"), nullable=True)
    hcp_name = Column(String(255), nullable=True)

    interaction_type = Column(String(100), nullable=True)  # e.g. Meeting, Call, Email, Event
    interaction_date = Column(String(100), nullable=True)  # kept as free text ("today", "2026-07-08")
    interaction_time = Column(String(50), nullable=True)

    attendees = Column(JSONB, nullable=True, default=list)
    topics = Column(JSONB, nullable=True, default=list)
    product = Column(String(255), nullable=True)
    sentiment = Column(String(50), nullable=True)  # Positive / Neutral / Negative
    materials = Column(JSONB, nullable=True, default=list)
    notes = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)

    status = Column(String(50), default="draft")  # draft | validated | saved

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    hcp = relationship("HCP", back_populates="interactions")
