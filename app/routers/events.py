from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user, get_admin_user
import cloudinary
import cloudinary.uploader
import uuid
import os

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

router = APIRouter(prefix="/events", tags=["Events"])

# ─── Get all events (with filtering) ────────────────────────
@router.get("/", response_model=list[schemas.EventResponse])
def get_events(
    category: Optional[str] = Query(None),
    available: Optional[bool] = Query(None),
    date: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("date"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Event).filter(models.Event.status == "active")

    if category:
        query = query.filter(models.Event.category == category)
    if available:
        query = query.filter(models.Event.seats_remaining > 0)
    if search:
        query = query.filter(models.Event.title.ilike(f"%{search}%"))
    if date:
        query = query.filter(models.Event.date >= date)
    if sort_by == "cost":
        query = query.order_by(models.Event.cost)
    else:
        query = query.order_by(models.Event.date)

    return query.all()

# ─── Get single event ────────────────────────────────────────
@router.get("/{event_id}", response_model=schemas.EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

# ─── Create event (admin only) ───────────────────────────────
@router.post("/", response_model=schemas.EventResponse, status_code=201)
def create_event(
    event: schemas.EventCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    new_event = models.Event(
        **event.model_dump(),
        seats_remaining=event.total_seats,
        organizer_id=current_user.id
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event

# ─── Update event (admin only) ───────────────────────────────
@router.put("/{event_id}", response_model=schemas.EventResponse)
def update_event(
    event_id: int,
    event_data: schemas.EventUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    for key, value in event_data.model_dump(exclude_unset=True).items():
        setattr(event, key, value)

    db.commit()
    db.refresh(event)
    return event

# ─── Cancel event (admin only) ───────────────────────────────
@router.delete("/{event_id}", status_code=200)
def cancel_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    event.status = "cancelled"
    db.commit()
    return {"message": "Event cancelled successfully"}

# ─── Upload poster (admin only) ──────────────────────────────
@router.post("/{event_id}/poster", response_model=schemas.EventResponse)
def upload_poster(
    event_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    result = cloudinary.uploader.upload(file.file)
    event.poster_url = result["secure_url"]
    db.commit()
    db.refresh(event)
    return event