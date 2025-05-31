from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from .models import Challenge, Event

class ChallengeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_challenge(self, challenge_data: dict) -> Challenge:
        challenge = Challenge(**challenge_data)
        self.session.add(challenge)
        await self.session.commit()
        await self.session.refresh(challenge)
        return challenge

    async def get_challenge(self, challenge_id: int) -> Challenge:
        query = select(Challenge).options(joinedload(Challenge.events)).where(Challenge.id == challenge_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all_challenges(self) -> list[Challenge]:
        query = select(Challenge).options(joinedload(Challenge.events))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_challenge(self, challenge_id: int, challenge_data: dict) -> Challenge:
        query = select(Challenge).where(Challenge.id == challenge_id)
        result = await self.session.execute(query)
        challenge = result.scalar_one_or_none()
        if challenge:
            for key, value in challenge_data.items():
                setattr(challenge, key, value)
            await self.session.commit()
            await self.session.refresh(challenge)
        return challenge

    async def delete_challenge(self, challenge_id: int) -> bool:
        query = select(Challenge).where(Challenge.id == challenge_id)
        result = await self.session.execute(query)
        challenge = result.scalar_one_or_none()
        if challenge:
            await self.session.delete(challenge)
            await self.session.commit()
            return True
        return False

class EventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_event(self, event_data: dict) -> Event:
        event = Event(**event_data)
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event

    async def get_event(self, event_id: int) -> Event:
        query = select(Event).where(Event.id == event_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_challenge_events(self, challenge_id: int) -> list[Event]:
        query = select(Event).where(Event.challenge_id == challenge_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_event(self, event_id: int, event_data: dict) -> Event:
        query = select(Event).where(Event.id == event_id)
        result = await self.session.execute(query)
        event = result.scalar_one_or_none()
        if event:
            for key, value in event_data.items():
                setattr(event, key, value)
            await self.session.commit()
            await self.session.refresh(event)
        return event

    async def delete_event(self, event_id: int) -> bool:
        query = select(Event).where(Event.id == event_id)
        result = await self.session.execute(query)
        event = result.scalar_one_or_none()
        if event:
            await self.session.delete(event)
            await self.session.commit()
            return True
        return False
