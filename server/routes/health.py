from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
from config.db import get_db
from routes.auth import get_current_user


router = APIRouter()


class HealthUpdate(BaseModel):
    steps: int | None = None
    water: int | None = None
    calories: int | None = None
    miles: float | None = None
    heartRate: int | None = None
    weight: float | None = None
    bmi: float | None = None
    mood: str | None = None
    activities: list[str] | None = None
    meals: list[str] | None = None
    symptoms: list[str] | None = None
    medications: list[str] | None = None
    reminders: list[str] | None = None


@router.get("/me")
async def get_health_me(current_user: dict = Depends(get_current_user)):
    db = get_db()
    user = await db.users.find_one({"email": current_user["email"].strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Return the user's health data directly from the user document
    return {
        "healthData": user.get("healthData", {}),
        "goals": user.get("goals", {}),
        "settings": user.get("settings", {})
    }

@router.get("/{email}")
async def get_health(email: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Return the user's health data directly from the user document
    return {
        "healthData": user.get("healthData", {}),
        "goals": user.get("goals", {}),
        "settings": user.get("settings", {})
    }


@router.patch("/me")
async def patch_today_health_me(payload: HealthUpdate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    users = db.users
    email = current_user["email"].strip().lower()
    user = await users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update the health data directly in the user document
    updates = {k: v for k, v in payload.dict(exclude_unset=True).items()}
    current_health_data = user.get("healthData", {})
    current_health_data.update(updates)
    
    await users.update_one({"_id": user["_id"]}, {"$set": {"healthData": current_health_data}})
    return {"success": True, "healthData": current_health_data}

@router.patch("/{email}")
async def patch_today_health(email: str, payload: HealthUpdate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    users = db.users
    email_n = email.strip().lower()
    user = await users.find_one({"email": email_n})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update the health data directly in the user document
    updates = {k: v for k, v in payload.dict(exclude_unset=True).items()}
    current_health_data = user.get("healthData", {})
    current_health_data.update(updates)
    
    await users.update_one({"_id": user["_id"]}, {"$set": {"healthData": current_health_data}})
    return {"success": True, "healthData": current_health_data}


# Blood pressure
class BPReading(BaseModel):
    systolic: int
    diastolic: int
    pulse: int | None = None
    notes: str | None = None
    timestamp: datetime | None = None


@router.post("/{email}/bp_readings")
async def add_bp_reading(email: str, payload: BPReading):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    readings = user.get("bpReadings", [])
    entry = {
        "systolic": payload.systolic,
        "diastolic": payload.diastolic,
        "pulse": payload.pulse,
        "notes": payload.notes,
        "timestamp": payload.timestamp or datetime.utcnow(),
    }
    readings.append(entry)
    await users.update_one({"_id": user["_id"]}, {"$set": {"bpReadings": readings}})
    return {"success": True, "reading": entry}


@router.get("/{email}/bp_readings")
async def get_bp_readings(email: str):
    db = get_db()
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    readings = sorted(user.get("bpReadings", []), key=lambda r: r.get("timestamp", 0), reverse=True)
    return readings


# Diabetes
class DiabetesReading(BaseModel):
    bloodGlucose: int
    readingType: str | None = "random"
    notes: str | None = None


@router.post("/{email}/diabetes")
async def add_diabetes_reading(email: str, payload: DiabetesReading):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    readings = user.get("diabetesReadings", [])
    entry = {
        "bloodGlucose": payload.bloodGlucose,
        "readingType": payload.readingType or "random",
        "notes": payload.notes,
        "timestamp": datetime.utcnow(),
    }
    readings.append(entry)
    await users.update_one({"_id": user["_id"]}, {"$set": {"diabetesReadings": readings}})
    return {"success": True, "reading": entry}


@router.get("/{email}/diabetes")
async def get_diabetes_readings(email: str):
    db = get_db()
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    readings = sorted(user.get("diabetesReadings", []), key=lambda r: r.get("timestamp", 0), reverse=True)
    return readings


# Medications
class Medication(BaseModel):
    name: str
    dosage: str | None = None
    frequency: str | None = None


@router.post("/{email}/medications")
async def add_medication(email: str, payload: Medication):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    meds = user.get("medications", [])
    entry = {
        "name": payload.name,
        "dosage": payload.dosage,
        "frequency": payload.frequency,
        "taken": 0,
        "total": 1,
        "timestamp": datetime.utcnow(),
    }
    meds.append(entry)
    await users.update_one({"_id": user["_id"]}, {"$set": {"medications": meds}})
    return {"success": True, "medication": entry}


@router.get("/{email}/medications")
async def get_medications(email: str):
    db = get_db()
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.get("medications", [])


class MedicationUpdate(BaseModel):
    taken: int


@router.patch("/{email}/medications/{med_id}")
async def update_medication(email: str, med_id: str, payload: MedicationUpdate):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    meds = user.get("medications", [])
    # naive update: index by order if no _id; else match by stringified _id
    updated = False
    for m in meds:
        if str(m.get("_id", "")) == med_id or m.get("name") == med_id:
            m["taken"] = payload.taken
            updated = True
            break
    if not updated:
        raise HTTPException(status_code=404, detail="Medication not found")
    await users.update_one({"_id": user["_id"]}, {"$set": {"medications": meds}})
    return {"success": True, "medication": meds}


# Sleep
class SleepPayload(BaseModel):
    bedtime: str | None = None
    wakeTime: str | None = None
    sleepDuration: float | None = None
    sleepQuality: int | None = None
    notes: str | None = None


@router.post("/{email}/sleep")
async def post_sleep(email: str, payload: SleepPayload):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    today = datetime.utcnow().date().isoformat()
    sleep_data = user.get("sleepData", [])
    entry = {
        "date": today,
        "bedtime": payload.bedtime,
        "wakeTime": payload.wakeTime,
        "sleepDuration": payload.sleepDuration,
        "sleepQuality": payload.sleepQuality,
        "notes": payload.notes,
    }
    idx = next((i for i, r in enumerate(sleep_data) if r.get("date") == today), None)
    if idx is None:
        sleep_data.append(entry)
    else:
        sleep_data[idx] = entry
    await users.update_one({"_id": user["_id"]}, {"$set": {"sleepData": sleep_data}})
    return {"success": True, "sleepData": entry}


@router.get("/{email}/sleep")
async def get_sleep(email: str):
    db = get_db()
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.get("sleepData", [])


# Mental health
class MentalPayload(BaseModel):
    mood: str
    anxietyLevel: int | None = None
    stressLevel: int | None = None
    notes: str | None = None


@router.post("/{email}/mental-health")
async def post_mental(email: str, payload: MentalPayload):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = user.get("mentalHealthData", [])
    entry = {
        "mood": payload.mood,
        "anxietyLevel": payload.anxietyLevel,
        "stressLevel": payload.stressLevel,
        "notes": payload.notes,
        "timestamp": datetime.utcnow(),
    }
    data.append(entry)
    await users.update_one({"_id": user["_id"]}, {"$set": {"mentalHealthData": data}})
    return {"success": True, "entry": entry}


@router.get("/{email}/mental-health")
async def get_mental(email: str):
    db = get_db()
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    entries = sorted(user.get("mentalHealthData", []), key=lambda r: r.get("timestamp", 0), reverse=True)
    return entries


# Goals
@router.patch("/{email}/goals")
async def patch_goals(email: str, goals: dict):
    db = get_db()
    users = db.users
    user = await users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    current = user.get("goals", {})
    current.update(goals)
    await users.update_one({"_id": user["_id"]}, {"$set": {"goals": current}})
    return {"success": True, "goals": current}


@router.get("/{email}/goals")
async def get_goals(email: str):
    db = get_db()
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.get("goals", {})


