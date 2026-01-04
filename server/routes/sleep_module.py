from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import uuid4
from config.db import get_db
from routes.auth import get_current_user


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
async def list_sleep(email: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.get("sleepData", [])


@router.post("/{email}")
async def create_sleep(email: str, payload: SleepCreate, current_user: dict = Depends(get_current_user)):
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
async def update_sleep(email: str, entry_id: str, payload: SleepUpdate, current_user: dict = Depends(get_current_user)):
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
async def delete_sleep(email: str, entry_id: str, current_user: dict = Depends(get_current_user)):
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


# /me endpoints for authenticated users
@router.get("/me")
async def list_sleep_me(current_user: dict = Depends(get_current_user)):
    db = get_db()
    user = await db.users.find_one({"email": current_user["email"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    sleep_data = user.get("sleepData", [])
    
    # Sort by date (most recent first) - ensure date field exists
    sleep_data.sort(key=lambda x: x.get("date", ""), reverse=True)
    
    return sleep_data


@router.post("/me")
async def create_sleep_me(payload: SleepCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": current_user["email"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    records = user.get("sleepData", [])
    
    # Ensure date is in YYYY-MM-DD format
    if payload.date:
        # Validate date format
        try:
            datetime.strptime(payload.date, "%Y-%m-%d")
            date = payload.date
        except ValueError:
            # If invalid format, use today's date
            date = datetime.utcnow().date().isoformat()
    else:
        date = datetime.utcnow().date().isoformat()
    
    entry = {
        "id": str(uuid4()),
        "date": date,  # Always in YYYY-MM-DD format
        "bedtime": payload.bedtime,
        "wakeTime": payload.wakeTime,
        "sleepDuration": payload.sleepDuration,
        "sleepQuality": payload.sleepQuality,
        "notes": payload.notes,
        "timestamp": datetime.utcnow().isoformat(),  # ISO format string for consistency
    }
    records.append(entry)
    await users.update_one({"_id": user["_id"]}, {"$set": {"sleepData": records}})
    return entry


