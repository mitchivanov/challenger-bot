from datetime import date
from typing import Optional

from .repository import ChallengeRepository, EventRepository
from .models import Challenge, Event

class ChallengeService:
    def __init__(self, challenge_repository: ChallengeRepository):
        self.repository = challenge_repository

    async def create_challenge(self, 
        title: str,
        description: str,
        start_date: date,
        end_date: date,
        requires_phone: bool,
        points_per_report: int,
        required_photos: int
    ) -> Challenge:
        challenge_data = {
            "title": title,
            "description": description,
            "start_date": start_date,
            "end_date": end_date,
            "requires_phone": requires_phone,
            "points_per_report": points_per_report,
            "required_photos": required_photos
        }
        return await self.repository.create_challenge(challenge_data)

    async def get_challenge(self, challenge_id: int) -> Optional[Challenge]:
        return await self.repository.get_challenge(challenge_id)

    async def get_all_challenges(self) -> list[Challenge]:
        return await self.repository.get_all_challenges()

    async def update_challenge(self, 
        challenge_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        requires_phone: Optional[bool] = None,
        points_per_report: Optional[int] = None,
        required_photos: Optional[int] = None
    ) -> Optional[Challenge]:
        challenge_data = {
            k: v for k, v in {
                "title": title,
                "description": description,
                "start_date": start_date,
                "end_date": end_date,
                "requires_phone": requires_phone,
                "points_per_report": points_per_report,
                "required_photos": required_photos
            }.items() if v is not None
        }
        return await self.repository.update_challenge(challenge_id, challenge_data)

    async def delete_challenge(self, challenge_id: int) -> bool:
        return await self.repository.delete_challenge(challenge_id)

class EventService:
    def __init__(self, event_repository: EventRepository):
        self.repository = event_repository

    async def create_event(self,
        challenge_id: int,
        title: str,
        description: str,
        start_date: date,
        end_date: date,
        requires_phone: bool,
        points_per_report: int,
        required_photos: int
    ) -> Event:
        event_data = {
            "challenge_id": challenge_id,
            "title": title,
            "description": description,
            "start_date": start_date,
            "end_date": end_date,
            "requires_phone": requires_phone,
            "points_per_report": points_per_report,
            "required_photos": required_photos
        }
        return await self.repository.create_event(event_data)

    async def get_event(self, event_id: int) -> Optional[Event]:
        return await self.repository.get_event(event_id)

    async def get_challenge_events(self, challenge_id: int) -> list[Event]:
        return await self.repository.get_challenge_events(challenge_id)

    async def update_event(self,
        event_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        requires_phone: Optional[bool] = None,
        points_per_report: Optional[int] = None,
        required_photos: Optional[int] = None
    ) -> Optional[Event]:
        event_data = {
            k: v for k, v in {
                "title": title,
                "description": description,
                "start_date": start_date,
                "end_date": end_date,
                "requires_phone": requires_phone,
                "points_per_report": points_per_report,
                "required_photos": required_photos
            }.items() if v is not None
        }
        return await self.repository.update_event(event_id, event_data)

    async def delete_event(self, event_id: int) -> bool:
        return await self.repository.delete_event(event_id)
