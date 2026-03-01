from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)

    registrations = relationship("Registration", back_populates="user")
    events = relationship("Event", back_populates="organizer")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    date = Column(DateTime, nullable=False)
    location = Column(String, nullable=False)
    total_seats = Column(Integer, nullable=False)
    seats_remaining = Column(Integer, nullable=False)
    cost = Column(Integer, default=0)
    contact_number = Column(String, nullable=True)
    poster_url = Column(String, nullable=True)
    category = Column(String, nullable=True)
    status = Column(String, default="active")  # active, cancelled, sold_out
    organizer_id = Column(Integer, ForeignKey("users.id"))

    organizer = relationship("User", back_populates="events")
    registrations = relationship("Registration", back_populates="event")


class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    booking_id = Column(String, unique=True, nullable=False)
    registered_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="registrations")
    event = relationship("Event", back_populates="registrations")