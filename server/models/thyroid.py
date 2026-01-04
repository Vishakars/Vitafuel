from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import uuid4
from config.db import get_db


router = APIRouter()


class ThyroidCreate(BaseModel):
    tsh: Optional[float] = None
    t3: Optional[float] = None
    t4: Optional[float] = None
    notes: Optional[str] = None
    timestamp: Optional[datetime] = None


class ThyroidUpdate(BaseModel):
    tsh: Optional[float] = None
    t3: Optional[float] = None
    t4: Optional[float] = None
    notes: Optional[str] = None


@router.get("/{email}")
async def list_thyroid(email: str):
    db = get_db()
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = sorted(user.get("thyroid", []), key=lambda r: r.get("timestamp", 0), reverse=True)
    return data


@router.post("/{email}")
async def create_thyroid(email: str, payload: ThyroidCreate):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = user.get("thyroid", [])
    entry = {
        "id": str(uuid4()),
        "tsh": payload.tsh,
        "t3": payload.t3,
        "t4": payload.t4,
        "notes": payload.notes,
        "timestamp": payload.timestamp or datetime.utcnow(),
    }
    data.append(entry)
    await users.update_one({"_id": user["_id"]}, {"$set": {"thyroid": data}})
    return entry


@router.patch("/{email}/{entry_id}")
async def update_thyroid(email: str, entry_id: str, payload: ThyroidUpdate):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = user.get("thyroid", [])
    for r in data:
        if r.get("id") == entry_id or str(r.get("_id", "")) == entry_id:
            updates = {k: v for k, v in payload.dict(exclude_unset=True).items()}
            r.update(updates)
            await users.update_one({"_id": user["_id"]}, {"$set": {"thyroid": data}})
            return r
    raise HTTPException(status_code=404, detail="Record not found")


@router.delete("/{email}/{entry_id}")
async def delete_thyroid(email: str, entry_id: str):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = user.get("thyroid", [])
    new_list = [r for r in data if r.get("id") != entry_id and str(r.get("_id", "")) != entry_id]
    if len(new_list) == len(data):
        raise HTTPException(status_code=404, detail="Record not found")
    await users.update_one({"_id": user["_id"]}, {"$set": {"thyroid": new_list}})
    return {"deleted": True}


