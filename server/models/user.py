from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Any, Dict
from datetime import datetime


class BloodPressureReading(BaseModel):
    systolic: int
    diastolic: int
    pulse: Optional[int] = None
    notes: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DiabetesReading(BaseModel):
    bloodGlucose: int
    readingType: str = "random"
    notes: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Medication(BaseModel):
    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    taken: int = 0
    total: int = 1
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SleepData(BaseModel):
    date: str
    bedtime: Optional[str] = None
    wakeTime: Optional[str] = None
    sleepDuration: Optional[float] = None
    sleepQuality: Optional[int] = None
    notes: Optional[str] = None


class WeightEntry(BaseModel):
    weight: float
    bmi: Optional[float] = None
    notes: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MenstruationEntry(BaseModel):
    cycleStart: Optional[datetime] = None
    cycleEnd: Optional[datetime] = None
    flowIntensity: Optional[str] = None
    symptoms: List[str] = []
    notes: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MentalHealthEntry(BaseModel):
    mood: str
    anxietyLevel: Optional[int] = None
    stressLevel: Optional[int] = None
    notes: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DailyHealth(BaseModel):
    date: str
    steps: int = 0
    water: int = 0
    calories: int = 0
    miles: float = 0
    heartRate: int = 0
    weight: float = 0
    bmi: float = 0
    mood: str = "😐"
    activities: List[str] = []
    meals: List[str] = []
    symptoms: List[str] = []
    reminders: List[str] = []


class Goals(BaseModel):
    dailySteps: int = 10000
    dailyWater: int = 2000
    dailyCalories: int = 2000
    targetWeight: Optional[float] = None
    targetBMI: Optional[float] = None


class Settings(BaseModel):
    dataRetentionDays: int = 365
    privacyLevel: str = "private"
    reminderSettings: Dict[str, bool] = {"medication": True, "water": True, "exercise": True}


class ProfileDemographics(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    dob: Optional[datetime] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None


class HealthDomain(BaseModel):
    name: str
    symptoms: List[Dict[str, Any]] = []
    data: Dict[str, Any] = {}

class Profile(BaseModel):
    demographics: ProfileDemographics = ProfileDemographics()
    healthDomains: List[HealthDomain] = [] # Now allows a list of HealthDomain objects
    avatarUrl: Optional[str] = None
    preferences: Dict[str, Any] = {"units": "metric", "notifications": True}


class UserModel(BaseModel):
    name: str
    email: EmailStr
    password: str
    profile: Profile = Profile()
    healthData: List[DailyHealth] = []
    bpReadings: List[BloodPressureReading] = []
    diabetesReadings: List[DiabetesReading] = []
    medications: List[Medication] = []
    sleepData: List[SleepData] = []
    weightHistory: List[WeightEntry] = []
    menstruationData: List[MenstruationEntry] = []
    mentalHealthData: List[MentalHealthEntry] = []
    goals: Goals = Goals()
    settings: Settings = Settings()

class UserUpdate(BaseModel):
    """
    Pydantic model for receiving profile updates from the frontend.
    """
    demographics: Optional[ProfileDemographics] = None
    # This correctly defines that the frontend sends a list of strings for healthDomains
    healthDomains: Optional[List[str]] = None 
