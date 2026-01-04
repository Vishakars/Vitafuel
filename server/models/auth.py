from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from config.db import get_db


router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
async def register_user(payload: RegisterRequest):
    db = get_db()
    users = db.users
    email = payload.email.lower().strip()
    existing = await users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed = pwd_context.hash(payload.password)
    await users.insert_one({
        "name": payload.name,
        "email": email,
        "password": hashed,
        "profile": {},
        "healthData": [],
        "bpReadings": [],
        "diabetesReadings": [],
        "medications": [],
        "sleepData": [],
        "weightHistory": [],
        "menstruationData": [],
        "mentalHealthData": [],
        "goals": {},
        "settings": {}
    })
    return {"message": "User registered successfully"}


@router.post("/login")
async def login_user(payload: LoginRequest):
    db = get_db()
    users = db.users
    email = payload.email.lower().strip()
    user = await users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    if not pwd_context.verify(payload.password, user.get("password", "")):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    return {"message": "Login successful", "email": user["email"], "name": user.get("name", "")} 


