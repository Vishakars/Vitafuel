# /server/routes/menstruation.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from routes.auth import get_current_user # Correct absolute import
from config.db import get_db

router = APIRouter()

# --- Pydantic Models for Data Validation ---
class Symptom(BaseModel):
    name: str
    intensity: Optional[int] = 0

class MenstruationEntry(BaseModel):
    date: str
    isMenstruating: bool
    symptoms: List[Symptom]
    flowIntensity: Optional[int] = 0
    notes: Optional[str] = ""
    timestamp: Optional[str] = None

# --- THE NEW, EFFICIENT ENDPOINTS ---

@router.get("/{email}", summary="Get all menstruation data for a user")
async def get_all_menstruation_data(email: str, current_user: dict = Depends(get_current_user)):
    """
    Fetches the entire menstruation_data object for a user.
    This is the only GET endpoint needed for this feature.
    """
    if email != current_user["email"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db = get_db()
    user_data = await db.health_data.find_one(
        {"email": email},
        {"_id": 0, "menstruation_data": 1} 
    )
    
    # Convert the dictionary of date-keyed entries into a list of entries
    if user_data and "menstruation_data" in user_data:
        menstruation_data = user_data["menstruation_data"]
        # Convert dict to list of entries with date included
        result = []
        for date, entry in menstruation_data.items():
            entry_with_date = {"date": date, **entry}
            result.append(entry_with_date)
        return result
    return []

@router.post("/{email}", summary="Save or update data for a specific date")
async def save_menstruation_entry(email: str, data: MenstruationEntry, current_user: dict = Depends(get_current_user)):
    """
    Saves or updates the data for a single, specific date.
    This is the only POST endpoint needed for this feature.
    """
    if email != current_user["email"]:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db = get_db()
    date_key = f"menstruation_data.{data.date}"
    
    # Save the complete entry data
    entry_data = {
        "isMenstruating": data.isMenstruating,
        "symptoms": [s.dict() for s in data.symptoms],
        "flowIntensity": getattr(data, 'flowIntensity', 0),
        "notes": getattr(data, 'notes', ''),
        "timestamp": getattr(data, 'timestamp', None)
    }
    
    await db.health_data.update_one(
        {"email": email},
        {"$set": {date_key: entry_data}},
        upsert=True
    )
    
    return {"message": f"Data for {data.date} saved successfully."}

@router.delete("/{email}", summary="Clear all menstruation data for a user")
async def clear_menstruation_data(email: str, current_user: dict = Depends(get_current_user)):
    """
    Clears all menstruation data for a user.
    """
    if email != current_user["email"]:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db = get_db()
    
    await db.health_data.update_one(
        {"email": email},
        {"$unset": {"menstruation_data": ""}}
    )
    
    return {"message": "All menstruation data cleared successfully."}

# --- TEST ENDPOINTS (NO AUTH REQUIRED) ---
@router.get("/test/{email}", summary="Test endpoint - Get menstruation data without auth")
async def test_get_menstruation_data(email: str):
    """Test endpoint to get menstruation data without authentication"""
    db = get_db()
    user_data = await db.health_data.find_one(
        {"email": email},
        {"_id": 0, "menstruation_data": 1} 
    )
    
    if user_data and "menstruation_data" in user_data:
        menstruation_data = user_data["menstruation_data"]
        result = []
        for date, entry in menstruation_data.items():
            entry_with_date = {"date": date, **entry}
            result.append(entry_with_date)
        return result
    return []

@router.post("/test/{email}", summary="Test endpoint - Save menstruation data without auth")
async def test_save_menstruation_entry(email: str, data: MenstruationEntry):
    """Test endpoint to save menstruation data without authentication"""
    db = get_db()
    date_key = f"menstruation_data.{data.date}"
    
    entry_data = {
        "isMenstruating": data.isMenstruating,
        "symptoms": [s.dict() for s in data.symptoms],
        "flowIntensity": getattr(data, 'flowIntensity', 0),
        "notes": getattr(data, 'notes', ''),
        "timestamp": getattr(data, 'timestamp', None)
    }
    
    await db.health_data.update_one(
        {"email": email},
        {"$set": {date_key: entry_data}},
        upsert=True
    )
    
    return {"message": f"Test data for {data.date} saved successfully."}

@router.delete("/test/{email}", summary="Test endpoint - Clear all menstruation data")
async def test_clear_menstruation_data(email: str):
    """Test endpoint to clear all menstruation data without authentication"""
    db = get_db()
    
    await db.health_data.update_one(
        {"email": email},
        {"$unset": {"menstruation_data": ""}}
    )
    
    return {"message": "All menstruation data cleared successfully."}

# --- END OF THE NEW, EFFICIENT ENDPOINTS ---