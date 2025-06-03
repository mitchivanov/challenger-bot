from datetime import date
from typing import Optional, List
import os
import aiofiles
from fastapi import UploadFile
from .repository import ChallengeRepository, EventRepository, ChallengeParticipantRepository, ReportRepository
from .models import Challenge, Event, UserReport, ReportPhoto
from .schemas import ReportCreate, Report
from datetime import datetime
import logging

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
        return await self.repository.create_challenge(
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            requires_phone=requires_phone,
            points_per_report=points_per_report,
            required_photos=required_photos
        )

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
        return await self.repository.update_challenge(challenge_id, **challenge_data)

    async def delete_challenge(self, challenge_id: int) -> bool:
        return await self.repository.delete_challenge(challenge_id)

class EventService:
    def __init__(self, event_repository: EventRepository):
        self.repository = event_repository

    async def create_event(self,
        challenge_id: int,
        title: str,
        description: str,
        date: date,
        points_per_report: int,
        required_photos: int
    ) -> Event:
        return await self.repository.create_event(
            challenge_id=challenge_id,
            title=title,
            description=description,
            date=date,
            points_per_report=points_per_report,
            required_photos=required_photos
        )

    async def get_event(self, event_id: int) -> Optional[Event]:
        return await self.repository.get_event(event_id)

    async def get_challenge_events(self, challenge_id: int):
        return await self.repository.get_challenge_events(challenge_id)

    async def update_event(self,
        event_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        date: Optional[date] = None,
        points_per_report: Optional[int] = None,
        required_photos: Optional[int] = None
    ) -> Optional[Event]:
        event_data = {
            k: v for k, v in {
                "title": title,
                "description": description,
                "date": date,
                "points_per_report": points_per_report,
                "required_photos": required_photos
            }.items() if v is not None
        }
        return await self.repository.update_event(event_id, **event_data)

    async def delete_event(self, event_id: int) -> bool:
        return await self.repository.delete_event(event_id)

class ChallengeParticipantService:
    def __init__(self, participant_repository: ChallengeParticipantRepository):
        self.repository = participant_repository

    async def join_challenge(self, user_id: int, challenge_id: int):
        return await self.repository.join_challenge(user_id, challenge_id)

    async def is_joined(self, user_id: int, challenge_id: int) -> bool:
        return await self.repository.is_joined(user_id, challenge_id)

class ReportService:
    def __init__(self, report_repository: ReportRepository, upload_dir: str = "uploads/reports"):
        self.report_repository = report_repository
        self.upload_dir = upload_dir

    async def create_report(self, report_data: ReportCreate) -> Report:
        logger = logging.getLogger(__name__)
        
        logger.info(f"Creating report: user_id={report_data.user_id}, challenge_id={report_data.challenge_id}, event_id={report_data.event_id}, report_date={report_data.report_date}")
        
        # Проверка: отчёт за этот день уже есть? (только для челленджей, не для мероприятий)
        if report_data.challenge_id and not report_data.event_id:
            logger.info(f"Checking for existing daily report for challenge {report_data.challenge_id}, date {report_data.report_date}")
            exists = await self.report_repository.exists_report_for_day(
                report_data.user_id, report_data.challenge_id, str(report_data.report_date)
            )
            if exists:
                logger.warning(f"Daily report already exists for user {report_data.user_id}, challenge {report_data.challenge_id}, date {report_data.report_date}")
                from fastapi import HTTPException
                raise HTTPException(status_code=409, detail="Отчёт за этот день уже отправлен")
        
        # Проверка: отчёт для этого мероприятия уже есть?
        if report_data.event_id:
            logger.info(f"Checking for existing event report for event {report_data.event_id}")
            event_reports = await self.report_repository.get_event_reports(report_data.event_id)
            user_event_reports = [r for r in event_reports if r.user_id == report_data.user_id]
            if user_event_reports:
                logger.warning(f"Event report already exists for user {report_data.user_id}, event {report_data.event_id}")
                from fastapi import HTTPException
                raise HTTPException(status_code=409, detail="Отчёт для этого мероприятия уже отправлен")
        
        report = await self.report_repository.create_report(
            user_id=report_data.user_id,
            text_content=report_data.text_content,
            challenge_id=report_data.challenge_id,
            event_id=report_data.event_id,
            report_date=report_data.report_date,
            created_at=datetime.utcnow()
        )
        # Начисляем баллы участнику челленджа
        if report_data.challenge_id:
            from .repository import ChallengeParticipantRepository, ChallengeRepository, EventRepository
            participant_repo = ChallengeParticipantRepository(self.report_repository.db)
            challenge_repo = ChallengeRepository(self.report_repository.db)
            
            participant = await participant_repo.get_participant(report_data.user_id, report_data.challenge_id)
            if participant:
                points_to_add = 0
                
                # Если отчет для мероприятия, используем очки мероприятия
                if report_data.event_id:
                    event_repo = EventRepository(self.report_repository.db)
                    event = await event_repo.get_event(report_data.event_id)
                    if event:
                        points_to_add = event.points_per_report
                else:
                    # Если отчет для челленджа, используем очки челленджа
                    challenge = await challenge_repo.get_challenge(report_data.challenge_id)
                    if challenge:
                        points_to_add = challenge.points_per_report
                
                # Начисляем очки
                if points_to_add > 0:
                    participant.points += points_to_add
                    await self.report_repository.db.commit()
        # Получаем полный отчет с связанными данными
        return await self.report_repository.get_report(report.id)

    async def upload_photos(self, report_id: int, photos: List[UploadFile]) -> List[ReportPhoto]:
        # Получаем отчет для проверки требований
        report = await self.report_repository.get_report(report_id)
        if not report:
            raise ValueError(f"Report with id {report_id} not found")
        
        # Определяем требуемое количество фотографий
        required_photos = 1  # По умолчанию
        if report.event_id:
            # Для мероприятий получаем требования из события
            from .repository import EventRepository
            event_repo = EventRepository(self.report_repository.db)
            event = await event_repo.get_event(report.event_id)
            if event:
                required_photos = event.required_photos
        elif report.challenge_id:
            # Для челленджей получаем требования из челленджа
            from .repository import ChallengeRepository
            challenge_repo = ChallengeRepository(self.report_repository.db)
            challenge = await challenge_repo.get_challenge(report.challenge_id)
            if challenge:
                required_photos = challenge.required_photos
        
        # Проверяем количество загружаемых фотографий
        if len(photos) != required_photos:
            raise ValueError(f"Expected {required_photos} photos, but got {len(photos)}")
        
        # Проверяем, нет ли уже загруженных фотографий для этого отчета
        existing_photos_count = len(report.photos) if report.photos else 0
        if existing_photos_count > 0:
            raise ValueError(f"Photos already uploaded for this report. Found {existing_photos_count} existing photos.")
        
        os.makedirs(self.upload_dir, exist_ok=True)
        
        photo_urls = []
        for photo in photos:
            # Генерируем уникальное имя файла
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"{report_id}_{timestamp}_{photo.filename}"
            filepath = os.path.join(self.upload_dir, filename)
            
            # Сохраняем файл
            async with aiofiles.open(filepath, 'wb') as f:
                content = await photo.read()
                await f.write(content)
            
            # Сохраняем относительный путь к файлу
            photo_urls.append(f"reports/{filename}")
        
        # Добавляем фотографии в базу данных
        photos = await self.report_repository.add_photos(report_id, photo_urls)
        return photos

    async def get_report(self, report_id: int, request=None) -> Optional[Report]:
        return await self.report_repository.get_report(report_id, request=request)

    async def get_user_reports(self, user_id: int, request=None) -> List[Report]:
        return await self.report_repository.get_user_reports(user_id, request=request)

    async def get_challenge_reports(self, challenge_id: int, request=None) -> List[Report]:
        return await self.report_repository.get_challenge_reports(challenge_id, request=request)

    async def get_event_reports(self, event_id: int) -> List[Report]:
        return await self.report_repository.get_event_reports(event_id)

    async def delete_report(self, report_id: int) -> bool:
        # Получаем отчет
        report = await self.report_repository.get_report(report_id)
        if not report:
            return False

        # Если отчет уже отклонен, ничего не делаем
        if report.rejected:
            return True

        # Если отчет связан с челленджем, уменьшаем баллы участника
        if report.challenge_id:
            from .repository import ChallengeParticipantRepository, ChallengeRepository, EventRepository
            participant_repo = ChallengeParticipantRepository(self.report_repository.db)
            challenge_repo = ChallengeRepository(self.report_repository.db)
            
            participant = await participant_repo.get_participant(report.user_id, report.challenge_id)
            if participant:
                points_to_subtract = 0
                
                # Если отчет для мероприятия, используем очки мероприятия
                if report.event_id:
                    event_repo = EventRepository(self.report_repository.db)
                    event = await event_repo.get_event(report.event_id)
                    if event:
                        points_to_subtract = event.points_per_report
                else:
                    # Если отчет для челленджа, используем очки челленджа
                    challenge = await challenge_repo.get_challenge(report.challenge_id)
                    if challenge:
                        points_to_subtract = challenge.points_per_report
                
                # Снимаем очки
                if points_to_subtract > 0:
                    participant.points = max(0, participant.points - points_to_subtract)
                    await self.report_repository.db.commit()

        # Помечаем отчет как отклоненный
        return await self.report_repository.reject_report(report_id)

    async def reject_report(self, report_id: int) -> Report:
        # Получаем отчет
        report = await self.report_repository.get_report(report_id)
        if not report:
            return None
        
        # Если отчет уже отклонен, возвращаем его как есть
        if report.rejected:
            return report
        
        # Отклоняем отчет в базе данных
        await self.report_repository.reject_report(report_id)
        
        # Если отчет связан с челленджем, уменьшаем баллы участника
        if report.challenge_id:
            from .repository import ChallengeParticipantRepository, ChallengeRepository, EventRepository
            participant_repo = ChallengeParticipantRepository(self.report_repository.db)
            challenge_repo = ChallengeRepository(self.report_repository.db)
            
            participant = await participant_repo.get_participant(report.user_id, report.challenge_id)
            if participant:
                points_to_subtract = 0
                
                # Если отчет для мероприятия, используем очки мероприятия
                if report.event_id:
                    event_repo = EventRepository(self.report_repository.db)
                    event = await event_repo.get_event(report.event_id)
                    if event:
                        points_to_subtract = event.points_per_report
                else:
                    # Если отчет для челленджа, используем очки челленджа
                    challenge = await challenge_repo.get_challenge(report.challenge_id)
                    if challenge:
                        points_to_subtract = challenge.points_per_report
                
                # Снимаем очки
                if points_to_subtract > 0:
                    participant.points = max(0, participant.points - points_to_subtract)
                    await self.report_repository.db.commit()
        
        # Возвращаем обновленный отчет
        return await self.report_repository.get_report(report_id)
