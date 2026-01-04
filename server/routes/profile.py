from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil
import uuid
from config.db import get_db
from models.user import UserUpdate, ProfileDemographics
from routes.auth import get_current_user  # resolves user from JWT

router = APIRouter()

# -------------------------------------------------------
#   PYDANTIC MODELS
# -------------------------------------------------------

class AddDomainPayload(BaseModel):
    healthDomain: str

class ProfileCreationPayload(BaseModel):
    email: Optional[str] = None               # ignored, backend uses JWT
    demographics: Optional[dict] = None
    goals: Optional[dict] = None
    healthDomains: Optional[List[str]] = None
    activities: Optional[List[str]] = None
    weeklyGoal: Optional[str] = None
    medical: Optional[dict] = None
    lifestyle: Optional[dict] = None
    preferences: Optional[dict] = None


# -------------------------------------------------------
#   GET PROFILE OF CURRENT AUTHENTICATED USER
# -------------------------------------------------------
@router.get("/me")
async def get_profile_me(
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    email = current_user["email"]
    doc = await db.users.find_one({"email": email}, {"_id": 0})

    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {
        "email": doc.get("email", ""),
        "name": doc.get("name", ""),
        "profile": doc.get("profile", {})
    }


# -------------------------------------------------------
#   CREATE / UPDATE PROFILE (SAFE MERGE UPDATE)
# -------------------------------------------------------
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_or_update_profile(
    payload: ProfileCreationPayload,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    email = current_user["email"]

    # Get existing user
    existing_user = await db.users.find_one({"email": email})
    existing_profile = existing_user.get("profile", {}) if existing_user else {}

    # Convert payload to dict (only provided fields)
    update_data = payload.dict(exclude_unset=True)

    # Convert string list -> object list for healthDomains
    if "healthDomains" in update_data:
        domains = update_data["healthDomains"]
        if isinstance(domains, list) and domains and isinstance(domains[0], str):
            update_data["healthDomains"] = [
                {"name": domain, "symptoms": [], "data": {}}
                for domain in domains
            ]

    # Merge existing profile with new values
    merged_profile = existing_profile.copy()

    for key, value in update_data.items():
        merged_profile[key] = value

    # Save merged profile
    result = await db.users.update_one(
        {"email": email},
        {"$set": {"profile": merged_profile}},
        upsert=True
    )

    return {"message": "Profile saved successfully", "profile": merged_profile}


# -------------------------------------------------------
#   ADD HEALTH DOMAIN
# -------------------------------------------------------
@router.post("/add-domain")
async def add_health_domain(
    payload: AddDomainPayload,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    email = current_user["email"]
    new_domain_name = payload.healthDomain

    if not new_domain_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Health domain name is required")

    new_domain_object = {"name": new_domain_name, "symptoms": [], "data": {}}

    result = await db.users.update_one(
        {"email": email},
        {"$push": {"profile.healthDomains": new_domain_object}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {"message": "Health domain added successfully"}


# -------------------------------------------------------
#   UPLOAD AVATAR
# -------------------------------------------------------
@router.patch("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    email = current_user["email"]
    user = await db.users.find_one({"email": email})

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    AVATAR_UPLOAD_DIR = "uploads/avatars"
    os.makedirs(AVATAR_UPLOAD_DIR, exist_ok=True)

    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_location = os.path.join(AVATAR_UPLOAD_DIR, unique_filename)

    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    avatar_url = f"/{AVATAR_UPLOAD_DIR}/{unique_filename}"

    await db.users.update_one(
        {"email": email},
        {"$set": {"profile.avatarUrl": avatar_url}}
    )

    return {"message": "Avatar uploaded successfully", "avatarUrl": avatar_url}


# -------------------------------------------------------
#   ADMIN GET PROFILE
# -------------------------------------------------------
@router.get("/{email}", response_model=dict)
async def get_user_profile(email: str, db=Depends(get_db)):
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    response_data = {
        "_id": str(user["_id"]),
        "email": user["email"],
        "name": user.get("name", ""),
        "profile": user.get("profile", {})
    }

    return response_data


# -------------------------------------------------------
#   ADMIN ADD HEALTH DOMAIN
# -------------------------------------------------------
@router.post("/{email}/add-domain")
async def admin_add_health_domain(email: str, payload: AddDomainPayload, db=Depends(get_db)):
    user_email = email.strip().lower()
    new_domain_name = payload.healthDomain

    if not new_domain_name:
        raise HTTPException(status_code=400, detail="Health domain name is required")

    new_domain_object = {"name": new_domain_name, "symptoms": [], "data": {}}

    result = await db.users.update_one(
        {"email": user_email},
        {"$push": {"profile.healthDomains": new_domain_object}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "Health domain added successfully for user"}


# -------------------------------------------------------
#   ADMIN AVATAR UPLOAD
# -------------------------------------------------------
@router.patch("/{email}/avatar")
async def admin_upload_avatar(email: str, file: UploadFile = File(...), db=Depends(get_db)):
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    AVATAR_UPLOAD_DIR = "uploads/avatars"
    os.makedirs(AVATAR_UPLOAD_DIR, exist_ok=True)

    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_location = os.path.join(AVATAR_UPLOAD_DIR, unique_filename)

    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    avatar_url = f"/{AVATAR_UPLOAD_DIR}/{unique_filename}"

    await db.users.update_one(
        {"email": email.strip().lower()},
        {"$set": {"profile.avatarUrl": avatar_url}}
    )

    return {"message": "Avatar uploaded successfully", "avatarUrl": avatar_url}


# -------------------------------------------------------
#   UPDATE HEALTH DOMAINS FOR CURRENT USER
# -------------------------------------------------------
@router.patch("/me/domains")
async def update_health_domains(payload: dict, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    user_email = current_user["email"].strip().lower()
    selected_domains = payload.get("selectedDomains", [])

    if not selected_domains:
        raise HTTPException(status_code=400, detail="Health domains are required")

    domain_objects = [{"name": domain, "symptoms": [], "data": {}} for domain in selected_domains]

    result = await db.users.update_one(
        {"email": user_email},
        {"$set": {"profile.healthDomains": domain_objects}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "Health domains updated successfully", "domains": selected_domains}

