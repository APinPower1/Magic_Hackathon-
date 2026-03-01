from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# ─── User Schemas ───────────────────────────────────────────
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    is_admin: bool

    class Config:
        from_attributes = True

# ─── Auth Schemas ────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# ─── Event Schemas ───────────────────────────────────────────
class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    date: datetime
    location: str
    total_seats: int
    cost: Optional[int] = 0
    contact_number: Optional[str] = None
    category: Optional[str] = None

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    location: Optional[str] = None
    total_seats: Optional[int] = None
    cost: Optional[int] = None
    contact_number: Optional[str] = None
    category: Optional[str] = None

class EventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    date: datetime
    location: str
    total_seats: int
    seats_remaining: int
    cost: int
    contact_number: Optional[str]
    poster_url: Optional[str]
    category: Optional[str]
    status: str
    organizer_id: int

    class Config:
        from_attributes = True

# ─── Registration Schemas ────────────────────────────────────
class RegistrationResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    booking_id: str
    registered_at: datetime

    class Config:
        from_attributes = True