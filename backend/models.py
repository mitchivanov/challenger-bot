from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, nullable=False, unique=True)
    phone_number = Column(String, nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    # Связь с отчетами
    reports = relationship("UserReport", back_populates="user")
    
class Challenge(Base):
    __tablename__ = "challenges"
    
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    requires_phone = Column(Boolean, default=False, nullable=False)
    points_per_report = Column(Integer, nullable=False)
    required_photos = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    # Связи
    events = relationship("Event", back_populates="challenge")
    reports = relationship("UserReport", back_populates="challenge")

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    requires_phone = Column(Boolean, default=False, nullable=False)
    points_per_report = Column(Integer, nullable=False)
    required_photos = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    # Связи
    challenge = relationship("Challenge", back_populates="events")
    reports = relationship("UserReport", back_populates="event")

class UserReport(Base):
    __tablename__ = "user_reports"
    
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    text_content = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    # Связи
    user = relationship("User", back_populates="reports")
    challenge = relationship("Challenge", back_populates="reports")
    event = relationship("Event", back_populates="reports")
    photos = relationship("ReportPhoto", back_populates="report")

class ReportPhoto(Base):
    __tablename__ = "report_photos"
    
    id = Column(Integer, primary_key=True, nullable=False)
    report_id = Column(Integer, ForeignKey("user_reports.id"), nullable=False)
    photo_url = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    # Связь
    report = relationship("UserReport", back_populates="photos")
    
