from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, date
from config.db import get_db
from routes.auth import get_current_user
from bson import ObjectId
import json


router = APIRouter()


def serialize_activity(activity: dict) -> dict:
    """Serialize activity document for JSON response"""
    if not activity:
        return activity
    
    result = {}
    for key, value in activity.items():
        if isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, date):
            result[key] = value.isoformat()
        else:
            result[key] = value
    return result


@router.get("/{email}")
async def get_analytics(email: str, current_user: dict = Depends(get_current_user)):
    """Get comprehensive analytics for a user"""
    if current_user["email"] != email:
        raise HTTPException(status_code=403, detail="Not authorized to view analytics for this user")
    
    db = get_db()
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get all user data
    health_data = user.get("healthData", {})
    diabetes_readings = user.get("diabetesReadings", [])
    bp_readings = user.get("bpReadings", [])
    mental_health_data = user.get("mentalHealthData", [])
    sleep_data = user.get("sleepData", [])
    
    # Get activity data from database
    activity_analytics = await _analyze_activities_from_db(db, email)
    
    # Calculate analytics
    analytics = {
        "overview": {
            "total_diabetes_readings": len(diabetes_readings),
            "total_bp_readings": len(bp_readings),
            "total_mental_health_entries": len(mental_health_data),
            "total_sleep_records": len(sleep_data),
            "total_activities": activity_analytics.get("total_activities", 0),
            "last_updated": datetime.utcnow().isoformat()
        },
        "diabetes": _analyze_diabetes(diabetes_readings),
        "blood_pressure": _analyze_blood_pressure(bp_readings),
        "mental_health": _analyze_mental_health(mental_health_data),
        "sleep": _analyze_sleep(sleep_data),
        "activities": activity_analytics,
        "health_trends": _analyze_health_trends(health_data)
    }
    
    return analytics


def _analyze_diabetes(readings: list) -> Dict[str, Any]:
    """Analyze diabetes readings"""
    if not readings:
        return {"status": "no_data", "message": "No diabetes readings available"}
    
    # Get recent readings (last 30 days)
    recent_readings = []
    cutoff_date = datetime.utcnow() - timedelta(days=30)
    
    for reading in readings:
        if isinstance(reading.get("timestamp"), str):
            try:
                reading_date = datetime.fromisoformat(reading["timestamp"].replace('Z', '+00:00'))
            except:
                continue
        else:
            reading_date = reading.get("timestamp", datetime.utcnow())
        
        if reading_date >= cutoff_date:
            recent_readings.append(reading)
    
    if not recent_readings:
        return {"status": "no_recent_data", "message": "No recent diabetes readings"}
    
    # Calculate averages
    glucose_values = [r["bloodGlucose"] for r in recent_readings if "bloodGlucose" in r]
    avg_glucose = sum(glucose_values) / len(glucose_values) if glucose_values else 0
    
    # Categorize readings
    normal_count = sum(1 for g in glucose_values if 70 <= g <= 100)
    prediabetic_count = sum(1 for g in glucose_values if 100 < g <= 125)
    diabetic_count = sum(1 for g in glucose_values if g > 125)
    
    return {
        "status": "data_available",
        "total_readings": len(recent_readings),
        "average_glucose": round(avg_glucose, 1),
        "readings_breakdown": {
            "normal": normal_count,
            "prediabetic": prediabetic_count,
            "diabetic": diabetic_count
        },
        "latest_reading": recent_readings[0] if recent_readings else None
    }


def _analyze_blood_pressure(readings: list) -> Dict[str, Any]:
    """Analyze blood pressure readings"""
    if not readings:
        return {"status": "no_data", "message": "No blood pressure readings available"}
    
    # Get recent readings (last 30 days)
    recent_readings = []
    cutoff_date = datetime.utcnow() - timedelta(days=30)
    
    for reading in readings:
        if isinstance(reading.get("timestamp"), str):
            try:
                reading_date = datetime.fromisoformat(reading["timestamp"].replace('Z', '+00:00'))
            except:
                continue
        else:
            reading_date = reading.get("timestamp", datetime.utcnow())
        
        if reading_date >= cutoff_date:
            recent_readings.append(reading)
    
    if not recent_readings:
        return {"status": "no_recent_data", "message": "No recent blood pressure readings"}
    
    # Calculate averages
    systolic_values = [r["systolic"] for r in recent_readings if "systolic" in r]
    diastolic_values = [r["diastolic"] for r in recent_readings if "diastolic" in r]
    
    avg_systolic = sum(systolic_values) / len(systolic_values) if systolic_values else 0
    avg_diastolic = sum(diastolic_values) / len(diastolic_values) if diastolic_values else 0
    
    # Categorize readings
    normal_count = sum(1 for s, d in zip(systolic_values, diastolic_values) 
                      if s < 120 and d < 80)
    elevated_count = sum(1 for s, d in zip(systolic_values, diastolic_values) 
                        if 120 <= s < 130 and d < 80)
    high_stage1_count = sum(1 for s, d in zip(systolic_values, diastolic_values) 
                           if (130 <= s < 140) or (80 <= d < 90))
    high_stage2_count = sum(1 for s, d in zip(systolic_values, diastolic_values) 
                           if s >= 140 or d >= 90)
    
    return {
        "status": "data_available",
        "total_readings": len(recent_readings),
        "average_systolic": round(avg_systolic, 1),
        "average_diastolic": round(avg_diastolic, 1),
        "readings_breakdown": {
            "normal": normal_count,
            "elevated": elevated_count,
            "high_stage1": high_stage1_count,
            "high_stage2": high_stage2_count
        },
        "latest_reading": recent_readings[0] if recent_readings else None
    }


def _analyze_mental_health(entries: list) -> Dict[str, Any]:
    """Analyze mental health entries"""
    if not entries:
        return {"status": "no_data", "message": "No mental health entries available"}
    
    # Get recent entries (last 30 days)
    recent_entries = []
    cutoff_date = datetime.utcnow() - timedelta(days=30)
    
    for entry in entries:
        if isinstance(entry.get("timestamp"), str):
            try:
                entry_date = datetime.fromisoformat(entry["timestamp"].replace('Z', '+00:00'))
            except:
                continue
        else:
            entry_date = entry.get("timestamp", datetime.utcnow())
        
        if entry_date >= cutoff_date:
            recent_entries.append(entry)
    
    if not recent_entries:
        return {"status": "no_recent_data", "message": "No recent mental health entries"}
    
    # Analyze mood patterns
    mood_counts = {}
    stress_levels = []
    anxiety_levels = []
    
    for entry in recent_entries:
        mood = entry.get("mood", "unknown")
        mood_counts[mood] = mood_counts.get(mood, 0) + 1
        
        if "stressLevel" in entry and entry["stressLevel"] is not None:
            stress_levels.append(entry["stressLevel"])
        
        if "anxietyLevel" in entry and entry["anxietyLevel"] is not None:
            anxiety_levels.append(entry["anxietyLevel"])
    
    avg_stress = sum(stress_levels) / len(stress_levels) if stress_levels else 0
    avg_anxiety = sum(anxiety_levels) / len(anxiety_levels) if anxiety_levels else 0
    
    return {
        "status": "data_available",
        "total_entries": len(recent_entries),
        "mood_distribution": mood_counts,
        "average_stress_level": round(avg_stress, 1) if stress_levels else None,
        "average_anxiety_level": round(avg_anxiety, 1) if anxiety_levels else None,
        "latest_entry": recent_entries[0] if recent_entries else None
    }


def _analyze_sleep(records: list) -> Dict[str, Any]:
    """Analyze sleep records"""
    if not records:
        return {"status": "no_data", "message": "No sleep records available"}
    
    # Get recent records (last 30 days)
    recent_records = []
    cutoff_date = datetime.utcnow() - timedelta(days=30)
    
    for record in records:
        if isinstance(record.get("date"), str):
            try:
                record_date = datetime.fromisoformat(record["date"]).date()
            except:
                continue
        else:
            record_date = record.get("date", datetime.utcnow().date())
        
        if record_date >= cutoff_date.date():
            recent_records.append(record)
    
    if not recent_records:
        return {"status": "no_recent_data", "message": "No recent sleep records"}
    
    # Calculate sleep statistics
    durations = [r["sleepDuration"] for r in recent_records if "sleepDuration" in r and r["sleepDuration"] is not None]
    qualities = [r["sleepQuality"] for r in recent_records if "sleepQuality" in r and r["sleepQuality"] is not None]
    
    avg_duration = sum(durations) / len(durations) if durations else 0
    avg_quality = sum(qualities) / len(qualities) if qualities else 0
    
    # Categorize sleep duration
    good_duration_count = sum(1 for d in durations if 7 <= d <= 9)
    short_duration_count = sum(1 for d in durations if d < 7)
    long_duration_count = sum(1 for d in durations if d > 9)
    
    return {
        "status": "data_available",
        "total_records": len(recent_records),
        "average_duration": round(avg_duration, 1) if durations else None,
        "average_quality": round(avg_quality, 1) if qualities else None,
        "duration_breakdown": {
            "good": good_duration_count,
            "short": short_duration_count,
            "long": long_duration_count
        },
        "latest_record": recent_records[0] if recent_records else None
    }


async def _analyze_activities_from_db(db, email: str, days: int = 30) -> Dict[str, Any]:
    """Analyze activities from the activity_logs collection"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Get activities from database
    activities = []
    async for activity in db.activity_logs.find({
        "user_email": email,
        "timestamp": {"$gte": cutoff_date}
    }).sort("timestamp", -1):
        activities.append(serialize_activity(activity))
    
    if not activities:
        return {
            "status": "no_data",
            "message": f"No activities found in the last {days} days",
            "total_activities": 0,
            "period_days": days
        }
    
    # Calculate statistics
    total_duration = sum(a.get("duration_minutes", 0) for a in activities)
    total_calories = sum(a.get("calories_burned", 0) for a in activities)
    total_distance = sum(a.get("distance_km", 0) for a in activities)
    avg_duration = total_duration / len(activities) if activities else 0
    avg_calories = total_calories / len(activities) if activities else 0
    
    # Group by activity type
    activity_types = {}
    for activity in activities:
        activity_type = activity.get("activity_type", "Unknown")
        if activity_type not in activity_types:
            activity_types[activity_type] = {
                "count": 0,
                "total_duration": 0,
                "total_calories": 0,
                "total_distance": 0
            }
        activity_types[activity_type]["count"] += 1
        activity_types[activity_type]["total_duration"] += activity.get("duration_minutes", 0)
        activity_types[activity_type]["total_calories"] += activity.get("calories_burned", 0)
        activity_types[activity_type]["total_distance"] += activity.get("distance_km", 0)
    
    # Group by intensity
    intensity_distribution = {}
    for activity in activities:
        intensity = activity.get("intensity", "moderate")
        intensity_distribution[intensity] = intensity_distribution.get(intensity, 0) + 1
    
    # Daily breakdown
    daily_stats = {}
    for activity in activities:
        activity_date = activity.get("date")
        if isinstance(activity_date, str):
            activity_date = datetime.fromisoformat(activity_date).date()
        elif isinstance(activity_date, datetime):
            activity_date = activity_date.date()
        
        date_str = activity_date.isoformat() if activity_date else "unknown"
        if date_str not in daily_stats:
            daily_stats[date_str] = {
                "count": 0,
                "duration": 0,
                "calories": 0,
                "distance": 0
            }
        daily_stats[date_str]["count"] += 1
        daily_stats[date_str]["duration"] += activity.get("duration_minutes", 0)
        daily_stats[date_str]["calories"] += activity.get("calories_burned", 0)
        daily_stats[date_str]["distance"] += activity.get("distance_km", 0)
    
    return {
        "status": "data_available",
        "total_activities": len(activities),
        "period_days": days,
        "total_duration_minutes": round(total_duration, 1),
        "total_calories_burned": round(total_calories, 1),
        "total_distance_km": round(total_distance, 2),
        "average_duration_per_activity": round(avg_duration, 1),
        "average_calories_per_activity": round(avg_calories, 1),
        "activity_types": activity_types,
        "intensity_distribution": intensity_distribution,
        "daily_stats": daily_stats,
        "recent_activities": activities[:10]  # Last 10 activities
    }


def _analyze_health_trends(health_data: dict) -> Dict[str, Any]:
    """Analyze general health trends"""
    if not health_data:
        return {"status": "no_data", "message": "No health data available"}
    
    trends = {
        "status": "data_available",
        "current_metrics": {
            "miles": health_data.get("miles", 0),
            "water": health_data.get("water", 0),
            "calories": health_data.get("calories", 0),
            "weight": health_data.get("weight", 0),
            "heartRate": health_data.get("heartRate", 0),
            "bmi": health_data.get("bmi", 0)
        },
        "activities_count": len(health_data.get("activities", [])),
        "meals_count": len(health_data.get("meals", [])),
        "symptoms_count": len(health_data.get("symptoms", [])),
        "reminders_count": len(health_data.get("reminders", []))
    }
    
    return trends


@router.get("/{email}/summary")
async def get_health_summary(email: str, current_user: dict = Depends(get_current_user)):
    """Get a quick health summary for dashboard"""
    if current_user["email"] != email:
        raise HTTPException(status_code=403, detail="Not authorized to view summary for this user")
    
    db = get_db()
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    health_data = user.get("healthData", {})
    
    # Get latest readings
    diabetes_readings = user.get("diabetesReadings", [])
    bp_readings = user.get("bpReadings", [])
    mental_health_data = user.get("mentalHealthData", [])
    sleep_data = user.get("sleepData", [])
    
    # Get today's activity summary from database
    today = datetime.now().date()
    today_activities = []
    async for activity in db.activity_logs.find({
        "user_email": email,
        "date": today
    }):
        today_activities.append(serialize_activity(activity))
    
    today_activity_duration = sum(a.get("duration_minutes", 0) for a in today_activities)
    today_activity_calories = sum(a.get("calories_burned", 0) for a in today_activities)
    
    summary = {
        "today": {
            "miles": health_data.get("miles", 0),
            "water": health_data.get("water", 0),
            "calories": health_data.get("calories", 0),
            "mood": health_data.get("mood", "😑"),
            "weight": health_data.get("weight", 0),
            "heartRate": health_data.get("heartRate", 0),
            "activity_duration_minutes": today_activity_duration,
            "activity_calories_burned": today_activity_calories,
            "activity_count": len(today_activities)
        },
        "latest_readings": {
            "diabetes": diabetes_readings[0] if diabetes_readings else None,
            "blood_pressure": bp_readings[0] if bp_readings else None,
            "mental_health": mental_health_data[0] if mental_health_data else None,
            "sleep": sleep_data[0] if sleep_data else None
        },
        "counts": {
            "diabetes_readings": len(diabetes_readings),
            "bp_readings": len(bp_readings),
            "mental_health_entries": len(mental_health_data),
            "sleep_records": len(sleep_data),
            "total_activities": await db.activity_logs.count_documents({"user_email": email})
        }
    }
    
    return summary


@router.get("/{email}/activities")
async def get_activity_analytics(
    email: str,
    days: int = 30,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get comprehensive activity analytics for a user"""
    if current_user["email"] != email:
        raise HTTPException(status_code=403, detail="Not authorized to view activity analytics for this user")
    
    return await _analyze_activities_from_db(db, email, days)


@router.get("/{email}/activities/historical")
async def get_historical_activities(
    email: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get historical activity data for analytics and recommendations"""
    if current_user["email"] != email:
        raise HTTPException(status_code=403, detail="Not authorized to view activities for this user")
    
    query = {"user_email": email}
    
    # Parse date range
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            query["date"] = {"$gte": start}
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
    
    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            if "date" in query:
                query["date"]["$lte"] = end
            else:
                query["date"] = {"$lte": end}
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
    
    # Get activities
    activities = []
    async for activity in db.activity_logs.find(query).sort("timestamp", -1).limit(limit):
        activities.append(serialize_activity(activity))
    
    return {
        "count": len(activities),
        "activities": activities,
        "query": {
            "start_date": start_date,
            "end_date": end_date,
            "limit": limit
        }
    }


@router.get("/me/activities")
async def get_activity_analytics_me(
    days: int = 30,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get activity analytics for the current authenticated user"""
    return await get_activity_analytics(current_user["email"], days, current_user, db)


@router.get("/me/activities/historical")
async def get_historical_activities_me(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get historical activity data for the current authenticated user"""
    return await get_historical_activities(
        current_user["email"], start_date, end_date, limit, current_user, db
    )
