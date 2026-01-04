from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from config.db import get_db


router = APIRouter()


class AnemiaEntry(BaseModel):
    hemoglobin: Optional[float] = None
    notes: Optional[str] = None


@router.post("/{email}")
async def add_anemia(email: str, payload: AnemiaEntry):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    anemia = user.get("anemia", [])
    entry = payload.dict(exclude_none=True)
    anemia.append(entry)
    await users.update_one({"_id": user["_id"]}, {"$set": {"anemia": anemia}})
    return {"message": "Entry saved", "entry": entry}


@router.get("/{email}")
async def get_anemia(email: str):
    db = get_db()
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"anemia": user.get("anemia", [])}


@router.delete("/{email}/{entry_id}")
async def delete_anemia(email: str, entry_id: str):
    # Entries don't have _id here; perform index-based delete if needed
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    anemia = user.get("anemia", [])
    new_list = [e for e in anemia if str(e.get("_id", "")) != entry_id]
    if len(new_list) == len(anemia):
        raise HTTPException(status_code=404, detail="Entry not found")
    await users.update_one({"_id": user["_id"]}, {"$set": {"anemia": new_list}})
    return {"message": "Entry deleted successfully"}


