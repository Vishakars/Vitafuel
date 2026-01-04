from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import uuid4
from config.db import get_db
from routes.auth import get_current_user


router = APIRouter()


class ThyroidCreate(BaseModel):
    tsh: Optional[float] = None
    t3: Optional[float] = None
    t4: Optional[float] = None
    weight: Optional[float] = None
    heartRate: Optional[int] = None
    sleep: Optional[int] = None
    energy: Optional[int] = None
    medication: Optional[str] = None
    symptoms: Optional[list] = None
    notes: Optional[str] = None
    timestamp: Optional[datetime] = None


class ThyroidUpdate(BaseModel):
    tsh: Optional[float] = None
    t3: Optional[float] = None
    t4: Optional[float] = None
    weight: Optional[float] = None
    heartRate: Optional[int] = None
    sleep: Optional[int] = None
    energy: Optional[int] = None
    medication: Optional[str] = None
    symptoms: Optional[list] = None
    notes: Optional[str] = None


@router.get("/me")
async def list_thyroid_me(current_user: dict = Depends(get_current_user)):
    db = get_db()
    user = await db.users.find_one({"email": current_user["email"].strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = sorted(user.get("thyroid", []), key=lambda r: r.get("timestamp", 0), reverse=True)
    return data

@router.get("/{email}")
async def list_thyroid(email: str):
    db = get_db()
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = sorted(user.get("thyroid", []), key=lambda r: r.get("timestamp", 0), reverse=True)
    return data


@router.post("/me")
async def create_thyroid_me(payload: ThyroidCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": current_user["email"].strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = user.get("thyroid", [])
    entry = {
        "id": str(uuid4()),
        "tsh": payload.tsh,
        "t3": payload.t3,
        "t4": payload.t4,
        "weight": payload.weight,
        "heartRate": payload.heartRate,
        "sleep": payload.sleep,
        "energy": payload.energy,
        "medication": payload.medication,
        "symptoms": payload.symptoms,
        "notes": payload.notes,
        "timestamp": payload.timestamp or datetime.utcnow(),
    }
    data.append(entry)
    await users.update_one({"_id": user["_id"]}, {"$set": {"thyroid": data}})
    return entry

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
        "weight": payload.weight,
        "heartRate": payload.heartRate,
        "sleep": payload.sleep,
        "energy": payload.energy,
        "medication": payload.medication,
        "symptoms": payload.symptoms,
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


@router.delete("/me/{entry_id}")
async def delete_thyroid_me(entry_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": current_user["email"].strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = user.get("thyroid", [])
    new_list = [r for r in data if r.get("id") != entry_id and str(r.get("_id", "")) != entry_id]
    if len(new_list) == len(data):
        raise HTTPException(status_code=404, detail="Record not found")
    await users.update_one({"_id": user["_id"]}, {"$set": {"thyroid": new_list}})
    return {"deleted": True}

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


