from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel

class ChallengeBase(BaseModel):
    title: str
    description: str
    start_date: date
    end_date: date
    requires_phone: bool = False
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
    created_at: datetime

    class Config:
        from_attributes = True

class EventBase(BaseModel):
    title: str
    description: str
    date: date
    points_per_report: int
    required_photos: int

class EventCreate(EventBase):
    challenge_id: int

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[date] = None
    points_per_report: Optional[int] = None
    required_photos: Optional[int] = None

class Event(EventBase):
    id: int
    challenge_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    telegram_id: str
    username: Optional[str] = None
    phone_number: Optional[str] = None

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ChallengeParticipantBase(BaseModel):
    user_id: int
    challenge_id: int

class ChallengeParticipantCreate(ChallengeParticipantBase):
    pass

class ChallengeParticipant(ChallengeParticipantBase):
    id: int
    joined_at: datetime
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    telegram_id: Optional[str] = None
    username: Optional[str] = None
    phone_number: Optional[str] = None

class ReportPhoto(BaseModel):
    id: int
    report_id: int
    photo_url: str
    created_at: datetime

    class Config:
        from_attributes = True

class ReportBase(BaseModel):
    user_id: int
    text_content: str
    challenge_id: Optional[int] = None
    event_id: Optional[int] = None
    report_date: date

class ReportCreate(ReportBase):
    pass

class Report(ReportBase):
    id: int
    created_at: datetime
    rejected: bool = False
    rejected_at: Optional[datetime] = None
    user: User
    photos: List[ReportPhoto]

    class Config:
        from_attributes = True

class ReportUpdate(BaseModel):
    rejected: Optional[bool] = None
