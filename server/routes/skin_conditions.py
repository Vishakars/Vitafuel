from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import uuid4
from config.db import get_db
from routes.auth import get_current_user


router = APIRouter()


class SkinCreate(BaseModel):
    condition: Optional[str] = None  # acne, eczema, etc
    severity: Optional[int] = None
    notes: Optional[str] = None
    timestamp: Optional[datetime] = None


class SkinUpdate(BaseModel):
    condition: Optional[str] = None
    severity: Optional[int] = None
    notes: Optional[str] = None


@router.get("/{email}")
async def list_skin(email: str):
    db = get_db()
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = sorted(user.get("skinConditions", []), key=lambda r: r.get("timestamp", 0), reverse=True)
    return data


@router.post("/{email}")
async def create_skin(email: str, payload: SkinCreate):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    records = user.get("skinConditions", [])
    entry = {
        "id": str(uuid4()),
        "condition": payload.condition,
        "severity": payload.severity,
        "notes": payload.notes,
        "timestamp": payload.timestamp or datetime.utcnow(),
    }
    records.append(entry)
    await users.update_one({"_id": user["_id"]}, {"$set": {"skinConditions": records}})
    return entry


@router.patch("/{email}/{entry_id}")
async def update_skin(email: str, entry_id: str, payload: SkinUpdate):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    records = user.get("skinConditions", [])
    for r in records:
        if r.get("id") == entry_id or str(r.get("_id", "")) == entry_id:
            updates = {k: v for k, v in payload.dict(exclude_unset=True).items()}
            r.update(updates)
            await users.update_one({"_id": user["_id"]}, {"$set": {"skinConditions": records}})
            return r
    raise HTTPException(status_code=404, detail="Record not found")


@router.delete("/{email}/{entry_id}")
async def delete_skin(email: str, entry_id: str):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    records = user.get("skinConditions", [])
    new_list = [r for r in records if r.get("id") != entry_id and str(r.get("_id", "")) != entry_id]
    if len(new_list) == len(records):
        raise HTTPException(status_code=404, detail="Record not found")
    await users.update_one({"_id": user["_id"]}, {"$set": {"skinConditions": new_list}})
    return {"deleted": True}


# /me endpoints for authenticated users
@router.get("/me")
async def list_skin_me(current_user: dict = Depends(get_current_user)):
    db = get_db()
    user = await db.users.find_one({"email": current_user["email"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = sorted(user.get("skinConditions", []), key=lambda r: r.get("timestamp", 0), reverse=True)
    return data


@router.post("/me")
async def create_skin_me(payload: SkinCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": current_user["email"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    records = user.get("skinConditions", [])
    entry = {
        "id": str(uuid4()),
        "condition": payload.condition,
        "severity": payload.severity,
        "notes": payload.notes,
        "timestamp": payload.timestamp or datetime.utcnow(),
    }
    records.append(entry)
    await users.update_one({"_id": user["_id"]}, {"$set": {"skinConditions": records}})
    return entry


