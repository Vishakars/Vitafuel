# /server/routes/auth.py

from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import os
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jose import JWTError, jwt
from config.db import get_db
from config.settings import get_settings

# --- CONFIGURATION ---
router = APIRouter()
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
settings = get_settings()

# --- JWT SECRET AND ALGORITHM ---
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # Token is valid for 24 hours

# --- PYDANTIC MODELS FOR REQUESTS AND TOKEN DATA ---
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class TokenData(BaseModel):
    email: str | None = None

# --- SECURITY DEPENDENCY & HELPER FUNCTIONS ---

# This tells FastAPI where to find the token (in the "Authorization: Bearer <token>" header)
# The `tokenUrl` should point to your login endpoint.
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def create_access_token(data: dict):
    """Creates a new JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(authorization: str = Header(None)):
    """
    This is the dependency that protected routes will use.
    It decodes the JWT token from the request header, validates it,
    and returns the corresponding user from the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not authorization or not authorization.startswith("Bearer "):
        raise credentials_exception
    
    token = authorization.split(" ")[1]
    
    try:
        # Decode the token to get the payload
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")  # "sub" is the standard claim for subject (the user's email)
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    # Get database connection and find the user
    db = get_db()
    user = await db.users.find_one({"email": token_data.email})
    if user is None:
        raise credentials_exception
    return user

# --- REGISTRATION AND LOGIN ENDPOINTS ---

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(payload: RegisterRequest):
    """Registers a new user in the database."""
    # Get database connection
    db = get_db()
    
    email = payload.email.lower().strip()
    
    if await db.users.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    # Hash the password
    hashed_password = pwd_context.hash(payload.password)
    
    await db.users.insert_one({
        "name": payload.name,
        "email": email,
        "password": hashed_password,
        "profile": {}, # Initialize with an empty profile
        "meals": [], # Initialize meals array for nutrition tracking
        "nutritionData": {} # Keep for backward compatibility
    })
    
    return {"message": "User registered successfully"}

@router.post("/login")
async def login_for_access_token(payload: LoginRequest):
    """Authenticates a user and returns a JWT access token."""
    # Get database connection
    db = get_db()
    
    email = payload.email.lower().strip()
    user = await db.users.find_one({"email": email})
    
    if not user or not pwd_context.verify(payload.password, user.get("password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create a token containing the user's email as the subject ("sub")
    access_token = create_access_token(data={"sub": user["email"]})
    
    # Return the token and user's email to the frontend
    return {"access_token": access_token, "token_type": "bearer", "email": user["email"]}

@router.post("/forgot-password")
async def forgot_password(payload: ForgotPasswordRequest):
    """Send password reset email to user"""
    db = get_db()
    email = payload.email.lower().strip()
    
    user = await db.users.find_one({"email": email})
    if not user:
        # Don't reveal if email exists or not for security
        return {"message": "If the email exists, a password reset link has been sent"}
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    reset_token_expiry = datetime.now(timezone.utc) + timedelta(hours=1)  # 1 hour expiry
    
    # Store reset token in database
    await db.users.update_one(
        {"email": email},
        {"$set": {
            "reset_token": reset_token,
            "reset_token_expiry": reset_token_expiry
        }}
    )
    
    # In a real application, you would send an email here
    # For now, we'll just return the token (in production, this should be sent via email)
    print(f"Password reset token for {email}: {reset_token}")
    
    return {"message": "If the email exists, a password reset link has been sent"}

@router.post("/reset-password")
async def reset_password(payload: ResetPasswordRequest):
    """Reset user password using reset token"""
    db = get_db()
    
    # Find user with valid reset token
    user = await db.users.find_one({
        "reset_token": payload.token,
        "reset_token_expiry": {"$gt": datetime.now(timezone.utc)}
    })
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Hash new password
    hashed_password = pwd_context.hash(payload.new_password)
    
    # Update password and clear reset token
    await db.users.update_one(
        {"email": user["email"]},
        {"$set": {"password": hashed_password}, "$unset": {"reset_token": "", "reset_token_expiry": ""}}
    )
    
    return {"message": "Password reset successfully"}

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {
        "email": current_user["email"],
        "name": current_user["name"],
        "profile": current_user.get("profile", {})
    }
