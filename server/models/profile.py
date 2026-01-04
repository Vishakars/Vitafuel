from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil
import uuid
from config.db import get_db
# This import will now work correctly
from models.user import UserUpdate 

router = APIRouter(
    prefix="/profile",
    tags=["profile"]
)

class ProfileUpsert(BaseModel):
    email: str
    demographics: Optional[dict] = None
    healthDomains: Optional[List[str]] = None
    preferences: Optional[dict] = None
    avatarUrl: Optional[str] = None


@router.post("/profile")
async def upsert_profile(payload: ProfileUpsert):
    db = get_db()
    users = db.users
    email = payload.email.strip().lower()
    user = await users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = user.get("profile", {})
    updates = payload.dict(exclude={"email"}, exclude_none=True)
    for key, value in updates.items():
        if isinstance(value, dict):
            profile[key] = {**profile.get(key, {}), **value}
        else:
            profile[key] = value

    await users.update_one({"_id": user["_id"]}, {"$set": {"profile": profile}})
    return {"message": "Profile updated successfully", "profile": profile}


@router.get("/profile/{email}")
async def get_profile(email: str):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    default_profile = {
        "demographics": {
            "firstName": (user.get("name", "").split(" ") or [""])[0],
            "lastName": " ".join(user.get("name", "").split(" ")[1:]) if user.get("name") else "",
            "dob": None,
            "gender": "",
            "height": ""
        },
        "healthDomains": []
    }
    merged = {**default_profile, **user.get("profile", {})}
    return {"email": user["email"], "name": user.get("name", ""), "profile": merged}


class DomainsUpdate(BaseModel):
    selectedDomains: List[str]


@router.patch("/profile/{email}/domains")
async def set_domains(email: str, payload: DomainsUpdate):
    db = get_db()
    users = db.users
    email_n = email.strip().lower()
    user = await users.find_one({"email": email_n})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    profile = user.get("profile", {})
    profile["healthDomains"] = payload.selectedDomains
    await users.update_one({"_id": user["_id"]}, {"$set": {"profile": profile}})
    return {"message": "Domains updated", "healthDomains": payload.selectedDomains}


@router.patch("/profile/{email}/avatar")
async def upload_avatar(email: str, avatar: UploadFile = File(...)):
    # save file to uploads/avatars and set avatarUrl
    db = get_db()
    users = db.users
    email_n = email.strip().lower()
    user = await users.find_one({"email": email_n})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    os.makedirs(os.path.join("uploads", "avatars"), exist_ok=True)
    safe_name = avatar.filename.replace(" ", "_")
    filepath = os.path.join("uploads", "avatars", safe_name)
    with open(filepath, "wb") as f:
        f.write(await avatar.read())

    url = f"/uploads/avatars/{safe_name}"
    profile = user.get("profile", {})
    profile["avatarUrl"] = url
    await users.update_one({"_id": user["_id"]}, {"$set": {"profile": profile}})
    return {"message": "Avatar uploaded", "avatarUrl": url}


