from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from config.db import get_db
from typing import List, Optional


router = APIRouter()


class Cycle(BaseModel):
    startDate: str
    length: int


@router.post("/{email}/menstruation")
async def add_cycle(email: str, payload: Cycle):
    db = get_db()
    users = db.users
    email_n = email.strip().lower()
    user = await users.find_one({"email": email_n})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    menstruation = user.get("menstruationData", [])
    menstruation.append({
        "cycleStart": datetime.fromisoformat(payload.startDate),
        "length": int(payload.length),
        "notes": f"Period of length {payload.length} started.",
        "timestamp": datetime.utcnow()
    })
    await users.update_one({"_id": user["_id"]}, {"$set": {"menstruationData": menstruation}})
    return {"success": True, "menstruation": menstruation}


@router.get("/{email}/menstruation")
async def get_cycles(email: str):
    db = get_db()
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"menstruation": user.get("menstruationData", [])}


class SymptomsPayload(BaseModel):
    date: str
    flowIntensity: Optional[str] = None
    symptoms: Optional[List[str]] = None
    notes: Optional[str] = None


@router.post("/{email}/symptoms")
async def set_symptoms(email: str, payload: SymptomsPayload):
    db = get_db()
    users = db.users
    email_n = email.strip().lower()
    user = await users.find_one({"email": email_n})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    health = user.get("healthData", [])
    idx = next((i for i, r in enumerate(health) if r.get("date") == payload.date), None)
    if idx is None:
        health.append({"date": payload.date, "symptoms": payload.symptoms or []})
    else:
        health[idx]["symptoms"] = payload.symptoms or []
    await users.update_one({"_id": user["_id"]}, {"$set": {"healthData": health}})
    return {"success": True, "healthData": health}


@router.get("/{email}/symptoms")
async def get_symptoms(email: str, date: Optional[str] = None):
    db = get_db()
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if date:
        day = next((r for r in user.get("healthData", []) if r.get("date") == date), None)
        return {"symptoms": (day.get("symptoms") if day else []) or []}
    return {"healthData": user.get("healthData", [])}


