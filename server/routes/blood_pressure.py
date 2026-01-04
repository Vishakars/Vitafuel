from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import uuid4
from config.db import get_db
from routes.auth import get_current_user


router = APIRouter()


class BPCreate(BaseModel):
    systolic: int
    diastolic: int
    pulse: Optional[int] = None
    notes: Optional[str] = None
    timestamp: Optional[datetime] = None


class BPUpdate(BaseModel):
    systolic: Optional[int] = None
    diastolic: Optional[int] = None
    pulse: Optional[int] = None
    notes: Optional[str] = None


@router.get("/me")
async def list_bp_me(current_user: dict = Depends(get_current_user)):
    db = get_db()
    user = await db.users.find_one({"email": current_user["email"].strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    readings = sorted(user.get("bpReadings", []), key=lambda r: r.get("timestamp", 0), reverse=True)
    return readings

@router.get("/{email}")
async def list_bp(email: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    readings = sorted(user.get("bpReadings", []), key=lambda r: r.get("timestamp", 0), reverse=True)
    return readings


@router.post("/me")
async def create_bp_me(payload: BPCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": current_user["email"].strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    readings = user.get("bpReadings", [])
    entry = {
        "id": str(uuid4()),
        "systolic": payload.systolic,
        "diastolic": payload.diastolic,
        "pulse": payload.pulse,
        "notes": payload.notes,
        "timestamp": payload.timestamp or datetime.utcnow(),
    }
    readings.append(entry)
    await users.update_one({"_id": user["_id"]}, {"$set": {"bpReadings": readings}})
    return entry

@router.post("/{email}")
async def create_bp(email: str, payload: BPCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    readings = user.get("bpReadings", [])
    entry = {
        "id": str(uuid4()),
        "systolic": payload.systolic,
        "diastolic": payload.diastolic,
        "pulse": payload.pulse,
        "notes": payload.notes,
        "timestamp": payload.timestamp or datetime.utcnow(),
    }
    readings.append(entry)
    await users.update_one({"_id": user["_id"]}, {"$set": {"bpReadings": readings}})
    return entry


@router.patch("/{email}/{entry_id}")
async def update_bp(email: str, entry_id: str, payload: BPUpdate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    readings = user.get("bpReadings", [])
    for r in readings:
        if r.get("id") == entry_id or str(r.get("_id", "")) == entry_id:
            updates = {k: v for k, v in payload.dict(exclude_unset=True).items()}
            r.update(updates)
            await users.update_one({"_id": user["_id"]}, {"$set": {"bpReadings": readings}})
            return r
    raise HTTPException(status_code=404, detail="Reading not found")


@router.delete("/{email}/{entry_id}")
async def delete_bp(email: str, entry_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    readings = user.get("bpReadings", [])
    new_list = [r for r in readings if r.get("id") != entry_id and str(r.get("_id", "")) != entry_id]
    if len(new_list) == len(readings):
        raise HTTPException(status_code=404, detail="Reading not found")
    await users.update_one({"_id": user["_id"]}, {"$set": {"bpReadings": new_list}})
    return {"deleted": True}


