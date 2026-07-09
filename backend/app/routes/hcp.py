from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.hcp import HCP
from app.schemas.hcp import HCPOut

router = APIRouter(prefix="/hcps", tags=["hcps"])


@router.get("", response_model=List[HCPOut])
def list_hcps(db: Session = Depends(get_db)):
    return db.query(HCP).order_by(HCP.name.asc()).all()
