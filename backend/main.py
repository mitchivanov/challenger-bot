from typing import List
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import os
from datetime import date

from .database import get_db, engine, Base, init_db
from .repository import ChallengeRepository, EventRepository, ChallengeParticipantRepository, ReportRepository
from .service import ChallengeService, EventService, ChallengeParticipantService, ReportService
from .schemas import Challenge, ChallengeCreate, ChallengeUpdate, Event, EventCreate, EventUpdate, User, UserCreate, UserUpdate, Report, ReportCreate, ReportPhoto, ReportUpdate
from . import models
from .models import User as UserModel

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3006", "https://lobster-civil-pigeon.ngrok-free.app", "https://libertylib.online"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Монтируем статические файлы
os.makedirs("uploads/reports", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Dependency
def get_challenge_service(db: AsyncSession = Depends(get_db)) -> ChallengeService:
    repository = ChallengeRepository(db)
    return ChallengeService(repository)

def get_event_service(db: AsyncSession = Depends(get_db)) -> EventService:
    repository = EventRepository(db)
    return EventService(repository)

def get_participant_service(db: AsyncSession = Depends(get_db)) -> ChallengeParticipantService:
    repository = ChallengeParticipantRepository(db)
    return ChallengeParticipantService(repository)

def get_report_service(db: AsyncSession = Depends(get_db)) -> ReportService:
    repository = ReportRepository(db)
    return ReportService(repository, upload_dir="/app/uploads/reports")

# Challenge routes
@app.post("/challenges/", response_model=Challenge)
async def create_challenge(
    challenge: ChallengeCreate,
    service: ChallengeService = Depends(get_challenge_service)
):
    return await service.create_challenge(
        title=challenge.title,
        description=challenge.description,
        start_date=challenge.start_date,
        end_date=challenge.end_date,
        requires_phone=challenge.requires_phone,
        points_per_report=challenge.points_per_report,
        required_photos=challenge.required_photos
    )

@app.get("/challenges/", response_model=List[Challenge])
async def read_challenges(service: ChallengeService = Depends(get_challenge_service)):
    return await service.get_all_challenges()

@app.get("/challenges/{challenge_id}", response_model=Challenge)
async def read_challenge(challenge_id: int, service: ChallengeService = Depends(get_challenge_service)):
    challenge = await service.get_challenge(challenge_id)
    if challenge is None:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return challenge

@app.patch("/challenges/{challenge_id}", response_model=Challenge)
async def update_challenge(
    challenge_id: int,
    challenge: ChallengeUpdate,
    service: ChallengeService = Depends(get_challenge_service)
):
    updated_challenge = await service.update_challenge(
        challenge_id=challenge_id,
        title=challenge.title,
        description=challenge.description,
        start_date=challenge.start_date,
        end_date=challenge.end_date,
        requires_phone=challenge.requires_phone,
        points_per_report=challenge.points_per_report,
        required_photos=challenge.required_photos
    )
    if updated_challenge is None:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return updated_challenge

@app.delete("/challenges/{challenge_id}")
async def delete_challenge(challenge_id: int, service: ChallengeService = Depends(get_challenge_service)):
    deleted = await service.delete_challenge(challenge_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return {"message": "Challenge deleted successfully"}

# Event routes
@app.post("/events/", response_model=Event)
async def create_event(event: EventCreate, service: EventService = Depends(get_event_service)):
    return await service.create_event(
        challenge_id=event.challenge_id,
        title=event.title,
        description=event.description,
        date=event.date,
        points_per_report=event.points_per_report,
        required_photos=event.required_photos
    )

@app.get("/challenges/{challenge_id}/events/", response_model=List[Event])
async def read_challenge_events(
    challenge_id: int,
    service: EventService = Depends(get_event_service)
):
    return await service.get_challenge_events(challenge_id)

@app.get("/events/{event_id}", response_model=Event)
async def read_event(event_id: int, service: EventService = Depends(get_event_service)):
    event = await service.get_event(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@app.patch("/events/{event_id}", response_model=Event)
async def update_event(
    event_id: int,
    event: EventUpdate,
    service: EventService = Depends(get_event_service)
):
    updated_event = await service.update_event(
        event_id=event_id,
        title=event.title,
        description=event.description,
        date=event.date,
        points_per_report=event.points_per_report,
        required_photos=event.required_photos
    )
    if updated_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return updated_event

@app.delete("/events/{event_id}")
async def delete_event(event_id: int, service: EventService = Depends(get_event_service)):
    deleted = await service.delete_event(event_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event deleted successfully"}

@app.get("/challenges/{challenge_id}/events", response_model=list[Event])
async def get_challenge_events(
    challenge_id: int,
    service: EventService = Depends(get_event_service)
):
    return await service.get_challenge_events(challenge_id)

@app.post("/challenges/{challenge_id}/join")
async def join_challenge(challenge_id: int, user_id: int, service: ChallengeParticipantService = Depends(get_participant_service)):
    return await service.join_challenge(user_id, challenge_id)

@app.get("/challenges/{challenge_id}/is_joined")
async def is_joined(challenge_id: int, user_id: int, service: ChallengeParticipantService = Depends(get_participant_service)):
    return {"joined": await service.is_joined(user_id, challenge_id)}

@app.get("/users/by_telegram_id/{telegram_id}", response_model=User)
async def get_user_by_telegram_id(telegram_id: str, db: AsyncSession = Depends(get_db)):
    q = select(UserModel).where(UserModel.telegram_id == telegram_id)
    result = await db.execute(q)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/users/", response_model=User)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    user_obj = UserModel(**user.dict())
    db.add(user_obj)
    await db.commit()
    await db.refresh(user_obj)
    return user_obj

@app.patch("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user: UserUpdate, db: AsyncSession = Depends(get_db)):
    q = select(UserModel).where(UserModel.id == user_id)
    result = await db.execute(q)
    user_obj = result.scalar_one_or_none()
    if not user_obj:
        return None
    for key, value in user.dict(exclude_unset=True).items():
        setattr(user_obj, key, value)
    await db.commit()
    await db.refresh(user_obj)
    return user_obj

# Report routes
@app.post("/reports/", response_model=Report)
async def create_report(
    report: ReportCreate,
    service: ReportService = Depends(get_report_service)
):
    return await service.create_report(report)

@app.post("/reports/{report_id}/photos", response_model=List[ReportPhoto])
async def upload_report_photos(
    report_id: int,
    photos: List[UploadFile] = File(...),
    service: ReportService = Depends(get_report_service)
):
    try:
        return await service.upload_photos(report_id, photos)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload photos: {str(e)}")

@app.get("/reports/user/{user_id}", response_model=List[Report])
async def get_user_reports(
    user_id: int,
    service: ReportService = Depends(get_report_service),
    request: Request = None
):
    return await service.get_user_reports(user_id, request=request)

@app.get("/reports/challenge/{challenge_id}", response_model=List[Report])
async def get_challenge_reports(
    challenge_id: int,
    service: ReportService = Depends(get_report_service),
    request: Request = None
):
    return await service.get_challenge_reports(challenge_id, request=request)

@app.get("/reports/event/{event_id}", response_model=List[Report])
async def get_event_reports(
    event_id: int,
    service: ReportService = Depends(get_report_service),
    request: Request = None
):
    return await service.get_event_reports(event_id)

@app.get("/challenges/{challenge_id}/participants/{user_id}/points")
async def get_participant_points(challenge_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    repo = ChallengeParticipantRepository(db)
    participant = await repo.get_participant(user_id, challenge_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    return {"points": participant.points}

@app.get("/challenges/{challenge_id}/leaderboard")
async def get_challenge_leaderboard(challenge_id: int, db: AsyncSession = Depends(get_db)):
    """Получить рейтинг участников челленджа"""
    repo = ChallengeParticipantRepository(db)
    participants = await repo.get_challenge_participants_with_users(challenge_id)
    
    # Сортируем по очкам в убывающем порядке
    leaderboard = []
    for participant in participants:
        leaderboard.append({
            "user_id": participant.user_id,
            "username": participant.user.username or "Аноним",
            "points": participant.points,
            "joined_at": participant.joined_at
        })
    
    # Сортируем по очкам (по убыванию) и дате присоединения (по возрастанию)
    leaderboard.sort(key=lambda x: (-x["points"], x["joined_at"]))
    
    return leaderboard

@app.delete("/reports/{report_id}")
async def delete_report(
    report_id: int,
    service: ReportService = Depends(get_report_service)
):
    deleted = await service.delete_report(report_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"message": "Report deleted successfully"}

@app.patch("/reports/{report_id}", response_model=Report)
async def reject_report(
    report_id: int,
    data: ReportUpdate,
    service: ReportService = Depends(get_report_service)
):
    if not data.rejected:
        raise HTTPException(status_code=400, detail="Nothing to update")
    
    print(f"Attempting to reject report {report_id}")  # Логирование для отладки
    
    updated_report = await service.reject_report(report_id)
    if not updated_report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    print(f"Report {report_id} rejected successfully, rejected={updated_report.rejected}")  # Логирование для отладки
    
    return updated_report
