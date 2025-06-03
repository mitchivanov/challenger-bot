from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, date
from fastapi import Request

from . import models

class ChallengeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_challenge(self, **kwargs):
        challenge = models.Challenge(**kwargs)
        self.db.add(challenge)
        await self.db.commit()
        await self.db.refresh(challenge)
        return challenge

    async def get_all_challenges(self):
        result = await self.db.execute(
            select(models.Challenge).options(selectinload(models.Challenge.events))
        )
        return result.scalars().all()

    async def get_challenge(self, challenge_id: int):
        result = await self.db.execute(
            select(models.Challenge)
            .options(selectinload(models.Challenge.events))
            .where(models.Challenge.id == challenge_id)
        )
        return result.scalar_one_or_none()

    async def update_challenge(self, challenge_id: int, **kwargs):
        challenge = await self.get_challenge(challenge_id)
        if challenge:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(challenge, key, value)
            await self.db.commit()
            await self.db.refresh(challenge)
        return challenge

    async def delete_challenge(self, challenge_id: int):
        challenge = await self.get_challenge(challenge_id)
        if challenge:
            await self.db.delete(challenge)
            await self.db.commit()
            return True
        return False

class EventRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_event(self, **kwargs):
        event = models.Event(**kwargs)
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def get_event(self, event_id: int):
        result = await self.db.execute(
            select(models.Event).where(models.Event.id == event_id)
        )
        return result.scalar_one_or_none()

    async def get_challenge_events(self, challenge_id: int):
        result = await self.db.execute(
            select(models.Event).where(models.Event.challenge_id == challenge_id)
        )
        return result.scalars().all()

    async def update_event(self, event_id: int, **kwargs):
        event = await self.get_event(event_id)
        if event:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(event, key, value)
            await self.db.commit()
            await self.db.refresh(event)
        return event

    async def delete_event(self, event_id: int):
        event = await self.get_event(event_id)
        if event:
            await self.db.delete(event)
            await self.db.commit()
            return True
        return False

class ChallengeParticipantRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def join_challenge(self, user_id: int, challenge_id: int):
        participant = models.ChallengeParticipant(
            user_id=user_id,
            challenge_id=challenge_id,
            joined_at=datetime.utcnow()
        )
        self.db.add(participant)
        await self.db.commit()
        await self.db.refresh(participant)
        return participant

    async def is_joined(self, user_id: int, challenge_id: int):
        result = await self.db.execute(
            select(models.ChallengeParticipant).where(
                models.ChallengeParticipant.user_id == user_id,
                models.ChallengeParticipant.challenge_id == challenge_id
            )
        )
        return result.scalar_one_or_none() is not None

    async def get_participant(self, user_id: int, challenge_id: int):
        result = await self.db.execute(
            select(models.ChallengeParticipant).where(
                models.ChallengeParticipant.user_id == user_id,
                models.ChallengeParticipant.challenge_id == challenge_id
            )
        )
        return result.scalar_one_or_none()

    async def get_challenge_participants_with_users(self, challenge_id: int):
        """Получает всех участников челленджа с информацией о пользователях"""
        result = await self.db.execute(
            select(models.ChallengeParticipant)
            .options(selectinload(models.ChallengeParticipant.user))
            .where(models.ChallengeParticipant.challenge_id == challenge_id)
            .order_by(models.ChallengeParticipant.points.desc())
        )
        return result.scalars().all()

class ReportRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_report(self, **kwargs):
        report = models.UserReport(**kwargs)
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def exists_report_for_day(self, user_id, challenge_id, report_date) -> bool:
        if isinstance(report_date, str):
            report_date = datetime.strptime(report_date, "%Y-%m-%d").date()
        result = await self.db.execute(
            select(models.UserReport).where(
                models.UserReport.user_id == user_id,
                models.UserReport.challenge_id == challenge_id,
                models.UserReport.report_date == report_date,
                models.UserReport.event_id.is_(None)  # Только обычные отчеты челленджа, не мероприятий
            )
        )
        return result.scalar_one_or_none() is not None

    async def add_photos(self, report_id: int, photo_urls: List[str]):
        photos = [
            models.ReportPhoto(report_id=report_id, photo_url=url)
            for url in photo_urls
        ]
        self.db.add_all(photos)
        await self.db.commit()
        return photos

    async def get_report(self, report_id: int, request: Request = None):
        result = await self.db.execute(
            select(models.UserReport)
            .options(selectinload(models.UserReport.user), selectinload(models.UserReport.photos))
            .where(models.UserReport.id == report_id)
        )
        return result.scalar_one_or_none()

    async def get_user_reports(self, user_id: int, request: Request = None):
        result = await self.db.execute(
            select(models.UserReport)
            .options(selectinload(models.UserReport.user), selectinload(models.UserReport.photos))
            .where(models.UserReport.user_id == user_id)
        )
        return result.scalars().all()

    async def get_challenge_reports(self, challenge_id: int, request: Request = None):
        result = await self.db.execute(
            select(models.UserReport)
            .options(selectinload(models.UserReport.user), selectinload(models.UserReport.photos))
            .where(models.UserReport.challenge_id == challenge_id)
        )
        return result.scalars().all()

    async def get_event_reports(self, event_id: int):
        result = await self.db.execute(
            select(models.UserReport)
            .options(selectinload(models.UserReport.user), selectinload(models.UserReport.photos))
            .where(models.UserReport.event_id == event_id)
        )
        return result.scalars().all()

    async def reject_report(self, report_id: int):
        result = await self.db.execute(
            select(models.UserReport).where(models.UserReport.id == report_id)
        )
        report = result.scalar_one_or_none()
        if not report:
            return False
        report.rejected = True
        report.rejected_at = datetime.utcnow()
        await self.db.commit()
        return True
