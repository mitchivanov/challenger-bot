from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String(255), unique=True, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    reports = relationship("UserReport", back_populates="user")

class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    requires_phone = Column(Boolean, default=False)
    points_per_report = Column(Integer, default=0)
    required_photos = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    events = relationship("Event", back_populates="challenge", cascade="all, delete-orphan")
    participants = relationship("ChallengeParticipant", back_populates="challenge", cascade="all, delete-orphan")
    reports = relationship("UserReport", back_populates="challenge", cascade="all, delete-orphan")

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    points_per_report = Column(Integer, nullable=False)
    required_photos = Column(Integer, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    challenge = relationship("Challenge", back_populates="events")
    reports = relationship("UserReport", back_populates="event", cascade="all, delete-orphan")

class ChallengeParticipant(Base):
    __tablename__ = "challenge_participants"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)
    points = Column(Integer, default=0)

    user = relationship("User")
    challenge = relationship("Challenge", back_populates="participants")

class UserReport(Base):
    __tablename__ = "user_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id", ondelete="CASCADE"), nullable=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=True)
    text_content = Column(Text, nullable=False)
    report_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    rejected = Column(Boolean, default=False)
    rejected_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="reports")
    challenge = relationship("Challenge", back_populates="reports")
    event = relationship("Event", back_populates="reports")
    photos = relationship("ReportPhoto", back_populates="report", cascade="all, delete-orphan")

class ReportPhoto(Base):
    __tablename__ = "report_photos"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("user_reports.id", ondelete="CASCADE"), nullable=False)
    photo_url = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    report = relationship("UserReport", back_populates="photos")
    
