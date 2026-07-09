import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Material(Base):
    """Detailing / promotional materials that can be shared with an HCP."""

    __tablename__ = "materials"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True, index=True)
    type = Column(String(100), nullable=True)  # e.g. Brochure, Sample, Leaflet, Visual Aid
