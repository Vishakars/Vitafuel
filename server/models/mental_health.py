from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import uuid4
from config.db import get_db


router = APIRouter()


class MentalCreate(BaseModel):
    mood: str
    anxietyLevel: Optional[int] = None
    stressLevel: Optional[int] = None
    notes: Optional[str] = None


class MentalUpdate(BaseModel):
    mood: Optional[str] = None
    anxietyLevel: Optional[int] = None
    stressLevel: Optional[int] = None
    notes: Optional[str] = None


@router.get("/{email}")
async def list_mental(email: str):
    db = get_db()
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    entries = sorted(user.get("mentalHealthData", []), key=lambda r: r.get("timestamp", 0), reverse=True)
    return entries


@router.post("/{email}")
async def create_mental(email: str, payload: MentalCreate):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    entries = user.get("mentalHealthData", [])
    entry = {
        "id": str(uuid4()),
        "mood": payload.mood,
        "anxietyLevel": payload.anxietyLevel,
        "stressLevel": payload.stressLevel,
        "notes": payload.notes,
        "timestamp": datetime.utcnow(),
    }
    entries.append(entry)
    await users.update_one({"_id": user["_id"]}, {"$set": {"mentalHealthData": entries}})
    return entry


@router.patch("/{email}/{entry_id}")
async def update_mental(email: str, entry_id: str, payload: MentalUpdate):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    entries = user.get("mentalHealthData", [])
    for r in entries:
        if r.get("id") == entry_id or str(r.get("_id", "")) == entry_id:
            updates = {k: v for k, v in payload.dict(exclude_unset=True).items()}
            r.update(updates)
            await users.update_one({"_id": user["_id"]}, {"$set": {"mentalHealthData": entries}})
            return r
    raise HTTPException(status_code=404, detail="Entry not found")


@router.delete("/{email}/{entry_id}")
async def delete_mental(email: str, entry_id: str):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    entries = user.get("mentalHealthData", [])
    new_list = [r for r in entries if r.get("id") != entry_id and str(r.get("_id", "")) != entry_id]
    if len(new_list) == len(entries):
        raise HTTPException(status_code=404, detail="Entry not found")
    await users.update_one({"_id": user["_id"]}, {"$set": {"mentalHealthData": new_list}})
    return {"deleted": True}


