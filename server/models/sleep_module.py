from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import uuid4
from config.db import get_db


router = APIRouter()


class SleepCreate(BaseModel):
    date: Optional[str] = None
    bedtime: Optional[str] = None
    wakeTime: Optional[str] = None
    sleepDuration: Optional[float] = None
    sleepQuality: Optional[int] = None
    notes: Optional[str] = None


class SleepUpdate(BaseModel):
    bedtime: Optional[str] = None
    wakeTime: Optional[str] = None
    sleepDuration: Optional[float] = None
    sleepQuality: Optional[int] = None
    notes: Optional[str] = None


@router.get("/{email}")
async def list_sleep(email: str):
    db = get_db()
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.get("sleepData", [])


@router.post("/{email}")
async def create_sleep(email: str, payload: SleepCreate):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    records = user.get("sleepData", [])
    date = payload.date or datetime.utcnow().date().isoformat()
    entry = {
        "id": str(uuid4()),
        "date": date,
        "bedtime": payload.bedtime,
        "wakeTime": payload.wakeTime,
        "sleepDuration": payload.sleepDuration,
        "sleepQuality": payload.sleepQuality,
        "notes": payload.notes,
    }
    # replace if same date exists
    idx = next((i for i, r in enumerate(records) if r.get("date") == date), None)
    if idx is None:
        records.append(entry)
    else:
        records[idx].update(entry)
    await users.update_one({"_id": user["_id"]}, {"$set": {"sleepData": records}})
    return entry


@router.patch("/{email}/{entry_id}")
async def update_sleep(email: str, entry_id: str, payload: SleepUpdate):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    records = user.get("sleepData", [])
    for r in records:
        if r.get("id") == entry_id or str(r.get("_id", "")) == entry_id:
            updates = {k: v for k, v in payload.dict(exclude_unset=True).items()}
            r.update(updates)
            await users.update_one({"_id": user["_id"]}, {"$set": {"sleepData": records}})
            return r
    raise HTTPException(status_code=404, detail="Record not found")


@router.delete("/{email}/{entry_id}")
async def delete_sleep(email: str, entry_id: str):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    records = user.get("sleepData", [])
    new_list = [r for r in records if r.get("id") != entry_id and str(r.get("_id", "")) != entry_id]
    if len(new_list) == len(records):
        raise HTTPException(status_code=404, detail="Record not found")
    await users.update_one({"_id": user["_id"]}, {"$set": {"sleepData": new_list}})
    return {"deleted": True}


