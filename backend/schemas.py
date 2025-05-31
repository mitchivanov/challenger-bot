from datetime import date
from typing import Optional
from pydantic import BaseModel

class ChallengeBase(BaseModel):
    title: str
    description: str
    start_date: date
    end_date: date
    requires_phone: bool
    points_per_report: int
    required_photos: int

class ChallengeCreate(ChallengeBase):
    pass

class ChallengeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    requires_phone: Optional[bool] = None
    points_per_report: Optional[int] = None
    required_photos: Optional[int] = None

class Challenge(ChallengeBase):
    id: int
    created_at: date

    class Config:
        from_attributes = True

class EventBase(BaseModel):
    title: str
    description: str
    start_date: date
    end_date: date
    requires_phone: bool
    points_per_report: int
    required_photos: int

class EventCreate(EventBase):
    challenge_id: int

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    requires_phone: Optional[bool] = None
    points_per_report: Optional[int] = None
    required_photos: Optional[int] = None

class Event(EventBase):
    id: int
    challenge_id: int
    created_at: date

    class Config:
        from_attributes = True
