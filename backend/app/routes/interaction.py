from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.interaction import Interaction
from app.models.hcp import HCP
from app.schemas.interaction import InteractionOut, InteractionUpdate, MANDATORY_FIELDS

router = APIRouter(prefix="/interaction", tags=["interaction"])


@router.get("", response_model=InteractionOut)
def get_interaction(session_id: str = Query(...), db: Session = Depends(get_db)):
    interaction = (
        db.query(Interaction)
        .filter(Interaction.session_id == session_id)
        .order_by(Interaction.created_at.desc())
        .first()
    )
    if interaction is None:
        raise HTTPException(status_code=404, detail="No interaction found for this session")
    return interaction


@router.post("/update", response_model=InteractionOut)
def update_interaction(
    session_id: str = Query(...),
    payload: InteractionUpdate = None,
    db: Session = Depends(get_db),
):
    """
    Direct structured patch endpoint. This is used internally by the /chat
    flow (and available for programmatic clients) — it is NOT exposed as a
    manual-edit form field in the UI, per product requirement that the form
    is AI-populated only.
    """
    interaction = (
        db.query(Interaction)
        .filter(Interaction.session_id == session_id)
        .order_by(Interaction.created_at.desc())
        .first()
    )
    if interaction is None:
        raise HTTPException(status_code=404, detail="No interaction found for this session")

    update_data = payload.dict(exclude_unset=True) if payload else {}
    for key, value in update_data.items():
        setattr(interaction, key, value)

    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction


@router.post("/save", response_model=InteractionOut)
def save_interaction(session_id: str = Query(...), db: Session = Depends(get_db)):
    interaction = (
        db.query(Interaction)
        .filter(Interaction.session_id == session_id)
        .order_by(Interaction.created_at.desc())
        .first()
    )
    if interaction is None:
        raise HTTPException(status_code=404, detail="No interaction found for this session")

    missing = [f for f in MANDATORY_FIELDS if not getattr(interaction, f)]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot save — missing mandatory fields: {', '.join(missing)}",
        )

    # Upsert HCP master record
    if interaction.hcp_name:
        hcp = db.query(HCP).filter(HCP.name == interaction.hcp_name).first()
        if hcp is None:
            hcp = HCP(name=interaction.hcp_name)
            db.add(hcp)
            db.commit()
            db.refresh(hcp)
        interaction.hcp_id = hcp.id

    interaction.status = "saved"
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction
