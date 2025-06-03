import aiohttp
from datetime import date
from config import BACKEND_URL
import os
from typing import List, Optional
import io
import logging

async def get_actual_challenges():
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{BACKEND_URL}/challenges/') as response:
            if response.status != 200:
                raise Exception("Failed to get challenges")
            challenges = await response.json()
            today = date.today().isoformat()
            return [
                c for c in challenges
                if c['start_date'] <= today <= c['end_date']
            ]

async def get_challenge(challenge_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{BACKEND_URL}/challenges/{challenge_id}') as response:
            if response.status != 200:
                raise Exception("Failed to get challenge")
            return await response.json()

async def get_user_by_telegram_id(telegram_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{BACKEND_URL}/users/by_telegram_id/{telegram_id}') as response:
            if response.status == 200:
                return await response.json()
            return None

async def create_user(telegram_id, username=None, phone_number=None):
    async with aiohttp.ClientSession() as session:
        data = {"telegram_id": str(telegram_id), "username": username, "phone_number": phone_number}
        async with session.post(f'{BACKEND_URL}/users/', json=data) as response:
            if response.status != 200:
                raise Exception("Failed to create user")
            return await response.json()

async def get_or_create_user(telegram_id, username=None, phone_number=None):
    user = await get_user_by_telegram_id(telegram_id)
    if user:
        return user
    return await create_user(telegram_id, username, phone_number)

async def update_user_phone(user_id, phone_number):
    async with aiohttp.ClientSession() as session:
        data = {"phone_number": phone_number}
        async with session.patch(f'{BACKEND_URL}/users/{user_id}', json=data) as response:
            if response.status != 200:
                raise Exception("Failed to update user phone")
            return await response.json()

async def is_joined(user_id, challenge_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{BACKEND_URL}/challenges/{challenge_id}/is_joined', params={"user_id": user_id}) as response:
            if response.status != 200:
                raise Exception("Failed to check join status")
            data = await response.json()
            return data.get("joined", False)

async def join_challenge(user_id, challenge_id):
    async with aiohttp.ClientSession() as session:
        async with session.post(f'{BACKEND_URL}/challenges/{challenge_id}/join', params={"user_id": user_id}) as response:
            if response.status != 200:
                raise Exception("Failed to join challenge")
            return await response.json()

async def get_challenge_events(challenge_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{BACKEND_URL}/challenges/{challenge_id}/events') as response:
            if response.status != 200:
                raise Exception("Failed to get events")
            return await response.json()

async def get_event(event_id):
    """Получает конкретное мероприятие по ID"""
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{BACKEND_URL}/events/{event_id}') as response:
            if response.status != 200:
                return None
            return await response.json()

async def get_user_event_reports(user_id: int, event_id: int) -> List[dict]:
    """Получает отчеты пользователя для конкретного мероприятия"""
    logger = logging.getLogger(__name__)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BACKEND_URL}/reports/event/{event_id}") as response:
            if response.status != 200:
                logger.warning(f"Failed to get event reports: status {response.status}")
                return []
            all_reports = await response.json()
            logger.info(f"Got {len(all_reports)} reports for event {event_id}")
            
            # Фильтруем по user_id
            user_reports = [r for r in all_reports if r.get('user_id') == user_id]
            logger.info(f"User {user_id} has {len(user_reports)} reports for event {event_id}")
            
            return user_reports

async def create_report(
    user_id: int,
    text_content: str,
    challenge_id: Optional[int] = None,
    event_id: Optional[int] = None,
    report_date: str = None,
    photos: List[str] = None,
    bot=None
) -> dict:
    """Создает отчет с фотографиями"""
    logger = logging.getLogger(__name__)
    
    async with aiohttp.ClientSession() as session:
        # Сначала создаем отчет
        report_data = {
            "user_id": user_id,
            "text_content": text_content,
            "challenge_id": challenge_id,
            "event_id": event_id,
            "report_date": report_date
        }
        logger.info(f"Creating report: {report_data}")
        
        async with session.post(f"{BACKEND_URL}/reports", json=report_data) as response:
            if response.status == 409:
                error_text = await response.text()
                logger.warning(f"Report conflict (409): {error_text}")
                raise Exception(f"Report already exists: {error_text}")
            elif response.status != 200:
                error_text = await response.text()
                logger.error(f"Failed to create report (status {response.status}): {error_text}")
                raise Exception(f"Failed to create report: {response.status} {error_text}")
            
            report = await response.json()
            logger.info(f"Report created successfully: {report['id']}")
            
            # Затем загружаем фотографии
            if photos and bot:
                logger.info(f"Uploading {len(photos)} photos for report {report['id']}")
                for photo_id in photos:
                    # Скачиваем файл через aiogram
                    photo_bytes = await bot.download(photo_id)
                    photo_bytes.seek(0)
                    data = aiohttp.FormData()
                    data.add_field(
                        'photos',
                        photo_bytes,
                        filename=f"{photo_id}.jpg",
                        content_type='image/jpeg'
                    )
                    async with session.post(
                        f"{BACKEND_URL}/reports/{report['id']}/photos",
                        data=data
                    ) as photo_response:
                        if photo_response.status != 200:
                            logger.warning(f"Failed to upload photo {photo_id}: {photo_response.status}")
                            continue
                        logger.info(f"Photo {photo_id} uploaded successfully")
            return report

async def get_user_reports(user_id: int) -> List[dict]:
    """Получает все отчеты пользователя"""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BACKEND_URL}/reports/user/{user_id}") as response:
            if response.status != 200:
                return []
            return await response.json()

async def get_challenge_reports(challenge_id: int) -> List[dict]:
    """Получает все отчеты по челленджу"""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BACKEND_URL}/reports/challenge/{challenge_id}") as response:
            if response.status != 200:
                return []
            return await response.json()

async def get_challenge_points(user_id: int, challenge_id: int) -> int:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BACKEND_URL}/challenges/{challenge_id}/participants/{user_id}/points") as response:
            if response.status == 200:
                data = await response.json()
                return data.get("points", 0)
            return 0

async def get_user_report_days(user_id: int, challenge_id: int) -> list:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BACKEND_URL}/reports/user/{user_id}") as response:
            if response.status != 200:
                return []
            reports = await response.json()
            # Фильтруем по challenge_id и собираем даты из report_date
            days = set()
            for r in reports:
                if r.get("challenge_id") == challenge_id and not r.get("event_id"):  # Только отчеты челленджа, не мероприятий
                    # Используем report_date вместо created_at
                    report_date = r.get("report_date")
                    if report_date:
                        days.add(report_date)
            return list(days)

async def get_challenge_leaderboard(challenge_id: int) -> List[dict]:
    """Получает рейтинг участников челленджа"""
    logger = logging.getLogger(__name__)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BACKEND_URL}/challenges/{challenge_id}/leaderboard") as response:
            if response.status != 200:
                logger.warning(f"Failed to get leaderboard: status {response.status}")
                return []
            leaderboard = await response.json()
            logger.info(f"Got leaderboard for challenge {challenge_id}: {len(leaderboard)} participants")
            return leaderboard 