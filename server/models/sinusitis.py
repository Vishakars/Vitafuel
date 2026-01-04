from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import uuid4
from config.db import get_db


router = APIRouter()


class SinusCreate(BaseModel):
    severity: Optional[int] = None
    notes: Optional[str] = None
    timestamp: Optional[datetime] = None


class SinusUpdate(BaseModel):
    severity: Optional[int] = None
    notes: Optional[str] = None


@router.get("/{email}")
async def list_sinus(email: str):
    db = get_db()
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = sorted(user.get("sinusitis", []), key=lambda r: r.get("timestamp", 0), reverse=True)
    return data


@router.post("/{email}")
async def create_sinus(email: str, payload: SinusCreate):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    records = user.get("sinusitis", [])
    entry = {
        "id": str(uuid4()),
        "severity": payload.severity,
        "notes": payload.notes,
        "timestamp": payload.timestamp or datetime.utcnow(),
    }
    records.append(entry)
    await users.update_one({"_id": user["_id"]}, {"$set": {"sinusitis": records}})
    return entry


@router.patch("/{email}/{entry_id}")
async def update_sinus(email: str, entry_id: str, payload: SinusUpdate):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    records = user.get("sinusitis", [])
    for r in records:
        if r.get("id") == entry_id or str(r.get("_id", "")) == entry_id:
            updates = {k: v for k, v in payload.dict(exclude_unset=True).items()}
            r.update(updates)
            await users.update_one({"_id": user["_id"]}, {"$set": {"sinusitis": records}})
            return r
    raise HTTPException(status_code=404, detail="Record not found")


@router.delete("/{email}/{entry_id}")
async def delete_sinus(email: str, entry_id: str):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    records = user.get("sinusitis", [])
    new_list = [r for r in records if r.get("id") != entry_id and str(r.get("_id", "")) != entry_id]
    if len(new_list) == len(records):
        raise HTTPException(status_code=404, detail="Record not found")
    await users.update_one({"_id": user["_id"]}, {"$set": {"sinusitis": new_list}})
    return {"deleted": True}


