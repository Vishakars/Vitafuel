from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import List, Optional
from config.db import get_db
from routes.auth import get_current_user
from bson import ObjectId

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

class ActivityType(BaseModel):
    name: str
    category: str  # e.g., "cardio", "strength", "flexibility", "sports"
    calories_per_minute: float
    description: Optional[str] = None

class ActivityLog(BaseModel):
    activity_type: str
    duration_minutes: int
    intensity: str = "moderate"  # low, moderate, high
    calories_burned: Optional[float] = None
    distance_km: Optional[float] = None
    notes: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class WorkoutPlan(BaseModel):
    name: str
    description: str
    activities: List[dict]  # List of activities with sets, reps, etc.
    estimated_duration: int  # minutes
    difficulty: str = "beginner"  # beginner, intermediate, advanced

class FitnessGoal(BaseModel):
    goal_type: str  # weight_loss, muscle_gain, endurance, flexibility
    target_value: float
    current_value: float
    target_date: date
    unit: str  # kg, lbs, minutes, etc.

@router.get("/activity-types")
async def get_activity_types():
    """Get all available activity types"""
    activity_types = [
        {
            "name": "Running",
            "category": "cardio",
            "calories_per_minute": 10.0,
            "description": "Outdoor or treadmill running"
        },
        {
            "name": "Walking",
            "category": "cardio",
            "calories_per_minute": 4.0,
            "description": "Brisk walking"
        },
        {
            "name": "Cycling",
            "category": "cardio",
            "calories_per_minute": 8.0,
            "description": "Bicycle riding"
        },
        {
            "name": "Swimming",
            "category": "cardio",
            "calories_per_minute": 12.0,
            "description": "Swimming laps"
        },
        {
            "name": "Weight Training",
            "category": "strength",
            "calories_per_minute": 6.0,
            "description": "Strength training with weights"
        },
        {
            "name": "Yoga",
            "category": "flexibility",
            "calories_per_minute": 3.0,
            "description": "Yoga practice"
        },
        {
            "name": "Pilates",
            "category": "flexibility",
            "calories_per_minute": 4.0,
            "description": "Pilates exercises"
        },
        {
            "name": "Basketball",
            "category": "sports",
            "calories_per_minute": 9.0,
            "description": "Basketball game or practice"
        },
        {
            "name": "Tennis",
            "category": "sports",
            "calories_per_minute": 8.0,
            "description": "Tennis match or practice"
        },
        {
            "name": "Dancing",
            "category": "cardio",
            "calories_per_minute": 7.0,
            "description": "Dance workout"
        }
    ]
    return activity_types

@router.post("/{email}/activities", status_code=status.HTTP_201_CREATED)
async def log_activity(
    email: str,
    activity: ActivityLog,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """Log a new activity for the user"""
    # Normalize emails for comparison
    user_email = current_user.get("email", "").strip().lower()
    requested_email = email.strip().lower()
    
    if user_email != requested_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to log activities for this user"
        )
    
    # Calculate calories burned if not provided
    if not activity.calories_burned:
        # Get activity type info
        activity_types = await get_activity_types()
        activity_info = next((a for a in activity_types if a["name"] == activity.activity_type), None)
        
        if activity_info:
            base_calories = activity_info["calories_per_minute"] * activity.duration_minutes
            
            # Adjust for intensity
            intensity_multiplier = {
                "low": 0.8,
                "moderate": 1.0,
                "high": 1.3
            }.get(activity.intensity, 1.0)
            
            activity.calories_burned = base_calories * intensity_multiplier
    
    activity_dict = activity.dict()
    # Normalize email to lowercase for consistent storage
    activity_dict["user_email"] = requested_email  # Use normalized email from above
    activity_dict["date"] = activity.timestamp.date()
    
    result = await db.activity_logs.insert_one(activity_dict)
    return {"message": "Activity logged successfully", "id": str(result.inserted_id)}

@router.get("/{email}/activities")
async def get_user_activities(
    email: str,
    date: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get activities for a user, optionally filtered by date"""
    # Normalize emails for comparison
    user_email = current_user.get("email", "").strip().lower()
    requested_email = email.strip().lower()
    
    if user_email != requested_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view activities for this user"
        )
    
    query = {"user_email": requested_email}  # Use normalized email
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
            query["date"] = target_date
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
    
    activities = []
    async for activity in db.activity_logs.find(query).sort("timestamp", -1):
        activities.append(serialize_activity(activity))
    
    return activities

@router.get("/{email}/activities/summary")
async def get_activity_summary(
    email: str,
    date: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get activity summary for a user"""
    # Normalize emails for comparison
    user_email = current_user.get("email", "").strip().lower()
    requested_email = email.strip().lower()
    
    if user_email != requested_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view activities for this user"
        )
    
    target_date = datetime.now().date()
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
    
    # Get activities for the date (use normalized email)
    activities = []
    async for activity in db.activity_logs.find({
        "user_email": requested_email,
        "date": target_date
    }):
        activities.append(serialize_activity(activity))
    
    # Calculate summary
    total_duration = sum(activity.get("duration_minutes", 0) for activity in activities)
    total_calories = sum(activity.get("calories_burned", 0) for activity in activities)
    total_distance = sum(activity.get("distance_km", 0) for activity in activities)
    
    # Group by activity type
    activity_types = {}
    for activity in activities:
        activity_type = activity.get("activity_type", "Unknown")
        if activity_type not in activity_types:
            activity_types[activity_type] = {
                "duration": 0,
                "calories": 0,
                "count": 0
            }
        activity_types[activity_type]["duration"] += activity.get("duration_minutes", 0)
        activity_types[activity_type]["calories"] += activity.get("calories_burned", 0)
        activity_types[activity_type]["count"] += 1
    
    return {
        "date": target_date.isoformat(),
        "total_duration_minutes": total_duration,
        "total_calories_burned": total_calories,
        "total_distance_km": total_distance,
        "activity_count": len(activities),
        "activity_types": activity_types,
        "activities": activities
    }

@router.post("/{email}/workout-plans", status_code=status.HTTP_201_CREATED)
async def create_workout_plan(
    email: str,
    workout_plan: WorkoutPlan,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """Create a new workout plan for the user"""
    if current_user["email"] != email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create workout plans for this user"
        )
    
    workout_dict = workout_plan.dict()
    workout_dict["user_email"] = email
    workout_dict["created_at"] = datetime.utcnow()
    
    result = await db.workout_plans.insert_one(workout_dict)
    return {"message": "Workout plan created successfully", "id": str(result.inserted_id)}

@router.get("/{email}/workout-plans")
async def get_workout_plans(
    email: str,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get all workout plans for a user"""
    if current_user["email"] != email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view workout plans for this user"
        )
    
    workout_plans = []
    async for plan in db.workout_plans.find({"user_email": email}).sort("created_at", -1):
        plan_dict = serialize_activity(plan)  # Reuse serialization function
        workout_plans.append(plan_dict)
    
    return workout_plans

@router.post("/{email}/fitness-goals", status_code=status.HTTP_201_CREATED)
async def create_fitness_goal(
    email: str,
    goal: FitnessGoal,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """Create a new fitness goal for the user"""
    if current_user["email"] != email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create fitness goals for this user"
        )
    
    goal_dict = goal.dict()
    goal_dict["user_email"] = email
    goal_dict["created_at"] = datetime.utcnow()
    goal_dict["progress_percentage"] = (goal.current_value / goal.target_value) * 100
    
    result = await db.fitness_goals.insert_one(goal_dict)
    return {"message": "Fitness goal created successfully", "id": str(result.inserted_id)}

@router.get("/{email}/fitness-goals")
async def get_fitness_goals(
    email: str,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get all fitness goals for a user"""
    if current_user["email"] != email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view fitness goals for this user"
        )
    
    goals = []
    async for goal in db.fitness_goals.find({"user_email": email}).sort("created_at", -1):
        # Update progress percentage
        goal["progress_percentage"] = (goal.get("current_value", 0) / goal.get("target_value", 1)) * 100
        goals.append(serialize_activity(goal))  # Reuse serialization function
    
    return goals

@router.patch("/{email}/fitness-goals/{goal_id}")
async def update_fitness_goal(
    email: str,
    goal_id: str,
    update_data: dict,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """Update a fitness goal"""
    if current_user["email"] != email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update fitness goals for this user"
        )
    
    # Update progress percentage if current_value is being updated
    if "current_value" in update_data:
        goal = await db.fitness_goals.find_one({"_id": ObjectId(goal_id), "user_email": email})
        if goal:
            target_value = goal.get("target_value", 1)
            update_data["progress_percentage"] = (update_data["current_value"] / target_value) * 100
    
    result = await db.fitness_goals.update_one(
        {"_id": ObjectId(goal_id), "user_email": email},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fitness goal not found"
        )
    
    return {"message": "Fitness goal updated successfully"}

@router.get("/{email}/stats/weekly")
async def get_weekly_stats(
    email: str,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get weekly activity statistics"""
    if current_user["email"] != email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view stats for this user"
        )
    
    from datetime import timedelta
    
    # Get date range for the past week
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=6)
    
    # Use normalized email for database query
    normalized_email = email.strip().lower()
    
    # Get activities for the week
    activities = []
    async for activity in db.activity_logs.find({
        "user_email": normalized_email,
        "date": {"$gte": start_date, "$lte": end_date}
    }):
        activities.append(serialize_activity(activity))
    
    # Calculate weekly totals
    total_duration = sum(activity.get("duration_minutes", 0) for activity in activities)
    total_calories = sum(activity.get("calories_burned", 0) for activity in activities)
    total_distance = sum(activity.get("distance_km", 0) for activity in activities)
    
    # Daily breakdown
    daily_stats = {}
    for i in range(7):
        current_date = start_date + timedelta(days=i)
        day_activities = [a for a in activities if a.get("date") == current_date]
        
        daily_stats[current_date.isoformat()] = {
            "duration": sum(a.get("duration_minutes", 0) for a in day_activities),
            "calories": sum(a.get("calories_burned", 0) for a in day_activities),
            "distance": sum(a.get("distance_km", 0) for a in day_activities),
            "activity_count": len(day_activities)
        }
    
    return {
        "week_start": start_date.isoformat(),
        "week_end": end_date.isoformat(),
        "total_duration_minutes": total_duration,
        "total_calories_burned": total_calories,
        "total_distance_km": total_distance,
        "total_activities": len(activities),
        "daily_stats": daily_stats
    }

# /me endpoints for authenticated users
@router.get("/me/activities/summary")
async def get_activity_summary_me(
    date: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get activity summary for the current authenticated user"""
    return await get_activity_summary(current_user["email"], date, current_user, db)

@router.get("/me/activities")
async def get_user_activities_me(
    date: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get activities for the current authenticated user"""
    return await get_user_activities(current_user["email"], date, current_user, db)

@router.post("/me/activities", status_code=status.HTTP_201_CREATED)
async def log_activity_me(
    activity: ActivityLog,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """Log a new activity for the current authenticated user"""
    return await log_activity(current_user["email"], activity, current_user, db)

@router.get("/me/stats/weekly")
async def get_weekly_stats_me(
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get weekly activity statistics for the current authenticated user"""
    return await get_weekly_stats(current_user["email"], current_user, db)


@router.delete("/{email}/activities/{activity_id}")
async def delete_activity_log(
    email: str,
    activity_id: str,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """Delete an activity log for a user"""
    if current_user["email"] != email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete activities for this user"
        )

    try:
        object_id = ObjectId(activity_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid activity ID")

    result = await db.activity_logs.delete_one({"_id": object_id, "user_email": email})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Activity not found")

    return {"deleted": True}


@router.delete("/me/activities/{activity_id}")
async def delete_activity_log_me(
    activity_id: str,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """Delete an activity log for the current authenticated user"""
    return await delete_activity_log(current_user["email"], activity_id, current_user, db)