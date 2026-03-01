from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user
import uuid

router = APIRouter(prefix="/events", tags=["Registrations"])

# ─── Register for event ──────────────────────────────────────
@router.post("/{event_id}/register", response_model=schemas.RegistrationResponse, status_code=201)
def register_for_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # 404 if event doesn't exist
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # 400 if event is cancelled
    if event.status == "cancelled":
        raise HTTPException(status_code=400, detail="Event is cancelled")

    # 409 if event is full
    if event.seats_remaining <= 0:
        raise HTTPException(status_code=409, detail="Event is full")

    # 409 if already registered
    existing = db.query(models.Registration).filter(
        models.Registration.user_id == current_user.id,
        models.Registration.event_id == event_id
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Already registered for this event")

    # Create registration
    registration = models.Registration(
        user_id=current_user.id,
        event_id=event_id,
        booking_id=str(uuid.uuid4())
    )
    db.add(registration)

    # Decrement seats
    event.seats_remaining -= 1
    if event.seats_remaining == 0:
        event.status = "sold_out"

    db.commit()
    db.refresh(registration)
    return registration

# ─── Cancel registration ─────────────────────────────────────
@router.delete("/{event_id}/cancel", status_code=200)
def cancel_registration(
    event_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # 404 if event doesn't exist
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # 404 if registration doesn't exist
    registration = db.query(models.Registration).filter(
        models.Registration.user_id == current_user.id,
        models.Registration.event_id == event_id
    ).first()
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")

    # Restore seat
    event.seats_remaining += 1
    if event.status == "sold_out":
        event.status = "active"

    db.delete(registration)
    db.commit()
    return {"message": "Registration cancelled successfully"}

# ─── Get registrants (admin only) ────────────────────────────
@router.get("/{event_id}/registrants")
def get_registrants(
    event_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    registrations = db.query(models.Registration).filter(
        models.Registration.event_id == event_id
    ).all()
    return registrations