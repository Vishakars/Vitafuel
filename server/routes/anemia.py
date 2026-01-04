from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import uuid4
from config.db import get_db
from routes.auth import get_current_user


router = APIRouter()


class AnemiaCreate(BaseModel):
    hemoglobin: Optional[float] = None
    ferritin: Optional[float] = None
    vitaminC: Optional[float] = None
    energy: Optional[int] = None
    supplement: Optional[str] = None
    symptoms: Optional[List[str]] = None
    notes: Optional[str] = None
    medications: Optional[str] = None
    selectedFoods: Optional[List[str]] = None
    totalIronToday: Optional[float] = None
    timestamp: Optional[datetime] = None


class AnemiaUpdate(BaseModel):
    hemoglobin: Optional[float] = None
    ferritin: Optional[float] = None
    vitaminC: Optional[float] = None
    energy: Optional[int] = None
    supplement: Optional[str] = None
    symptoms: Optional[List[str]] = None
    notes: Optional[str] = None
    medications: Optional[str] = None
    selectedFoods: Optional[List[str]] = None
    totalIronToday: Optional[float] = None


@router.get("/me")
async def list_anemia_me(current_user: dict = Depends(get_current_user)):
    db = get_db()
    user = await db.users.find_one({"email": current_user["email"].strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = sorted(user.get("anemia", []), key=lambda r: r.get("timestamp", 0), reverse=True)
    return data

@router.get("/{email}")
async def list_anemia(email: str):
    db = get_db()
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = sorted(user.get("anemia", []), key=lambda r: r.get("timestamp", 0), reverse=True)
    return data


@router.post("/me")
async def create_anemia_me(payload: AnemiaCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": current_user["email"].strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = user.get("anemia", [])
    entry = {
        "id": str(uuid4()),
        "hemoglobin": payload.hemoglobin,
        "ferritin": payload.ferritin,
        "vitaminC": payload.vitaminC,
        "energy": payload.energy,
        "supplement": payload.supplement,
        "symptoms": payload.symptoms,
        "notes": payload.notes,
        "medications": payload.medications,
        "selectedFoods": payload.selectedFoods,
        "totalIronToday": payload.totalIronToday,
        "timestamp": payload.timestamp or datetime.utcnow(),
    }
    data.append(entry)
    await users.update_one({"_id": user["_id"]}, {"$set": {"anemia": data}})
    return entry

@router.post("/{email}")
async def create_anemia(email: str, payload: AnemiaCreate):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = user.get("anemia", [])
    entry = {
        "id": str(uuid4()),
        "hemoglobin": payload.hemoglobin,
        "ferritin": payload.ferritin,
        "vitaminC": payload.vitaminC,
        "energy": payload.energy,
        "supplement": payload.supplement,
        "symptoms": payload.symptoms,
        "notes": payload.notes,
        "medications": payload.medications,
        "selectedFoods": payload.selectedFoods,
        "totalIronToday": payload.totalIronToday,
        "timestamp": payload.timestamp or datetime.utcnow(),
    }
    data.append(entry)
    await users.update_one({"_id": user["_id"]}, {"$set": {"anemia": data}})
    return entry


@router.patch("/{email}/{entry_id}")
async def update_anemia(email: str, entry_id: str, payload: AnemiaUpdate):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = user.get("anemia", [])
    for r in data:
        if r.get("id") == entry_id or str(r.get("_id", "")) == entry_id:
            updates = {k: v for k, v in payload.dict(exclude_unset=True).items()}
            r.update(updates)
            await users.update_one({"_id": user["_id"]}, {"$set": {"anemia": data}})
            return r
    raise HTTPException(status_code=404, detail="Record not found")


@router.delete("/me/{entry_id}")
async def delete_anemia_me(entry_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": current_user["email"].strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = user.get("anemia", [])
    new_list = [r for r in data if r.get("id") != entry_id and str(r.get("_id", "")) != entry_id]
    if len(new_list) == len(data):
        raise HTTPException(status_code=404, detail="Record not found")
    await users.update_one({"_id": user["_id"]}, {"$set": {"anemia": new_list}})
    return {"deleted": True}

@router.delete("/me")
async def delete_all_anemia_me(current_user: dict = Depends(get_current_user)):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": current_user["email"].strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await users.update_one({"_id": user["_id"]}, {"$set": {"anemia": []}})
    return {"deleted": True, "count": len(user.get("anemia", []))}

@router.delete("/{email}/{entry_id}")
async def delete_anemia(email: str, entry_id: str):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = user.get("anemia", [])
    new_list = [r for r in data if r.get("id") != entry_id and str(r.get("_id", "")) != entry_id]
    if len(new_list) == len(data):
        raise HTTPException(status_code=404, detail="Record not found")
    await users.update_one({"_id": user["_id"]}, {"$set": {"anemia": new_list}})
    return {"deleted": True}


