from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db
from .repository import ChallengeRepository, EventRepository
from .service import ChallengeService, EventService
from .schemas import Challenge, ChallengeCreate, ChallengeUpdate, Event, EventCreate, EventUpdate

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_challenge_service(db: AsyncSession = Depends(get_db)) -> ChallengeService:
    repository = ChallengeRepository(db)
    return ChallengeService(repository)

def get_event_service(db: AsyncSession = Depends(get_db)) -> EventService:
    repository = EventRepository(db)
    return EventService(repository)

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
async def create_event(
    event: EventCreate,
    service: EventService = Depends(get_event_service)
):
    return await service.create_event(
        challenge_id=event.challenge_id,
        title=event.title,
        description=event.description,
        start_date=event.start_date,
        end_date=event.end_date,
        requires_phone=event.requires_phone,
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
        start_date=event.start_date,
        end_date=event.end_date,
        requires_phone=event.requires_phone,
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
