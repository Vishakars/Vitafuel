from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import uuid4
from config.db import get_db


router = APIRouter()


class DiabetesCreate(BaseModel):
    bloodGlucose: int
    readingType: Optional[str] = "random"
    notes: Optional[str] = None


class DiabetesUpdate(BaseModel):
    bloodGlucose: Optional[int] = None
    readingType: Optional[str] = None
    notes: Optional[str] = None


@router.get("/{email}")
async def list_diabetes(email: str):
    db = get_db()
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    readings = sorted(user.get("diabetesReadings", []), key=lambda r: r.get("timestamp", 0), reverse=True)
    return readings


@router.post("/{email}")
async def create_diabetes(email: str, payload: DiabetesCreate):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    readings = user.get("diabetesReadings", [])
    entry = {
        "id": str(uuid4()),
        "bloodGlucose": payload.bloodGlucose,
        "readingType": payload.readingType or "random",
        "notes": payload.notes,
        "timestamp": datetime.utcnow(),
    }
    readings.append(entry)
    await users.update_one({"_id": user["_id"]}, {"$set": {"diabetesReadings": readings}})
    return entry


@router.patch("/{email}/{entry_id}")
async def update_diabetes(email: str, entry_id: str, payload: DiabetesUpdate):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    readings = user.get("diabetesReadings", [])
    for r in readings:
        if r.get("id") == entry_id or str(r.get("_id", "")) == entry_id:
            updates = {k: v for k, v in payload.dict(exclude_unset=True).items()}
            r.update(updates)
            await users.update_one({"_id": user["_id"]}, {"$set": {"diabetesReadings": readings}})
            return r
    raise HTTPException(status_code=404, detail="Reading not found")


@router.delete("/{email}/{entry_id}")
async def delete_diabetes(email: str, entry_id: str):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    readings = user.get("diabetesReadings", [])
    new_list = [r for r in readings if r.get("id") != entry_id and str(r.get("_id", "")) != entry_id]
    if len(new_list) == len(readings):
        raise HTTPException(status_code=404, detail="Reading not found")
    await users.update_one({"_id": user["_id"]}, {"$set": {"diabetesReadings": new_list}})
    return {"deleted": True}


