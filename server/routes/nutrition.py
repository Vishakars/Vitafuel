from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, date
from typing import List, Optional
from config.db import get_db
from routes.auth import get_current_user
from utils.nutrition_api import search_nutrition_online
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# --- PYDANTIC MODELS ---

class FoodItem(BaseModel):
    name: str
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: Optional[float] = 0
    sugar: Optional[float] = 0
    sodium: Optional[float] = 0
    serving_size: str = "100g"
    brand: Optional[str] = None

class MealEntry(BaseModel):
    food_item: FoodItem
    quantity: float  # in servings
    meal_type: str  # breakfast, lunch, dinner, snack
    notes: Optional[str] = None

class DailyNutrition(BaseModel):
    date: str  # YYYY-MM-DD format
    meals: List[MealEntry] = []
    water_intake: float = 0  # in ml
    notes: Optional[str] = None

class NutritionGoal(BaseModel):
    daily_calories: int = 2000
    daily_protein: float = 50  # in grams
    daily_carbs: float = 250  # in grams
    daily_fat: float = 65  # in grams
    daily_fiber: float = 25  # in grams
    daily_water: float = 2000  # in ml

# --- ROUTE DEFINITIONS ---

@router.get("/food-database")
async def search_food_database(query: str = "", limit: int = 20, online: bool = True):
    """
    Search the food database for items
    First searches local database, then falls back to online API if not found
    
    Args:
        query: Search term for food items
        limit: Maximum number of results to return
        online: Whether to search online if not found locally (default: True)
    """
    # Basic food database - local cache for common items
    food_database = [
        {
            "name": "Apple",
            "calories": 52,
            "protein": 0.3,
            "carbs": 14,
            "fat": 0.2,
            "fiber": 2.4,
            "sugar": 10,
            "sodium": 1,
            "serving_size": "100g",
            "brand": None,
            "source": "local"
        },
        {
            "name": "Banana",
            "calories": 89,
            "protein": 1.1,
            "carbs": 23,
            "fat": 0.3,
            "fiber": 2.6,
            "sugar": 12,
            "sodium": 1,
            "serving_size": "100g",
            "brand": None,
            "source": "local"
        },
        {
            "name": "Chicken Breast",
            "calories": 165,
            "protein": 31,
            "carbs": 0,
            "fat": 3.6,
            "fiber": 0,
            "sugar": 0,
            "sodium": 74,
            "serving_size": "100g",
            "brand": None,
            "source": "local"
        },
        {
            "name": "Brown Rice",
            "calories": 111,
            "protein": 2.6,
            "carbs": 23,
            "fat": 0.9,
            "fiber": 1.8,
            "sugar": 0.4,
            "sodium": 5,
            "serving_size": "100g",
            "brand": None,
            "source": "local"
        },
        {
            "name": "Greek Yogurt",
            "calories": 59,
            "protein": 10,
            "carbs": 3.6,
            "fat": 0.4,
            "fiber": 0,
            "sugar": 3.6,
            "sodium": 36,
            "serving_size": "100g",
            "brand": None,
            "source": "local"
        },
        {
            "name": "Almonds",
            "calories": 579,
            "protein": 21,
            "carbs": 22,
            "fat": 50,
            "fiber": 12,
            "sugar": 4.4,
            "sodium": 1,
            "serving_size": "100g",
            "brand": None,
            "source": "local"
        },
        {
            "name": "Salmon",
            "calories": 208,
            "protein": 25,
            "carbs": 0,
            "fat": 12,
            "fiber": 0,
            "sugar": 0,
            "sodium": 44,
            "serving_size": "100g",
            "brand": None,
            "source": "local"
        },
        {
            "name": "Broccoli",
            "calories": 34,
            "protein": 2.8,
            "carbs": 7,
            "fat": 0.4,
            "fiber": 2.6,
            "sugar": 1.5,
            "sodium": 33,
            "serving_size": "100g",
            "brand": None,
            "source": "local"
        },
        {
            "name": "Eggs",
            "calories": 155,
            "protein": 13,
            "carbs": 1.1,
            "fat": 11,
            "fiber": 0,
            "sugar": 1.1,
            "sodium": 124,
            "serving_size": "100g",
            "brand": None,
            "source": "local"
        },
        {
            "name": "Oatmeal",
            "calories": 68,
            "protein": 2.4,
            "carbs": 12,
            "fat": 1.4,
            "fiber": 1.7,
            "sugar": 0.6,
            "sodium": 4,
            "serving_size": "100g",
            "brand": None,
            "source": "local"
        }
    ]
    
    # Search local database first
    if query:
        filtered_foods = [food for food in food_database if query.lower() in food["name"].lower()]
    else:
        filtered_foods = food_database
    
    # If no results found locally and online search is enabled, search online
    if len(filtered_foods) == 0 and query and online:
        logger.info(f"No local results for '{query}', searching online...")
        try:
            online_results = await search_nutrition_online(query, limit)
            if online_results:
                logger.info(f"Found {len(online_results)} results online for '{query}'")
                return online_results[:limit]
            else:
                logger.info(f"No online results found for '{query}'")
        except Exception as e:
            logger.error(f"Error searching online: {e}")
            # Continue to return empty local results
    
    return filtered_foods[:limit]

@router.get("/{email}/nutrition/{date}")
async def get_daily_nutrition(email: str, date: str, current_user: dict = Depends(get_current_user)):
    """Get nutrition data for a specific date"""
    # Ensure user can only access their own data
    if current_user["email"].lower() != email.strip().lower():
        raise HTTPException(status_code=403, detail="Not authorized to view nutrition data for this user")
    
    db = get_db()
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    nutrition_data = user.get("nutritionData", {})
    daily_data = nutrition_data.get(date, {
        "date": date,
        "meals": [],
        "water_intake": 0,
        "notes": ""
    })
    
    # Calculate totals
    totals = {
        "calories": 0,
        "protein": 0,
        "carbs": 0,
        "fat": 0,
        "fiber": 0,
        "sugar": 0,
        "sodium": 0
    }
    
    for meal in daily_data.get("meals", []):
        food = meal.get("food_item", {})
        quantity = meal.get("quantity", 1)
        totals["calories"] += food.get("calories", 0) * quantity
        totals["protein"] += food.get("protein", 0) * quantity
        totals["carbs"] += food.get("carbs", 0) * quantity
        totals["fat"] += food.get("fat", 0) * quantity
        totals["fiber"] += food.get("fiber", 0) * quantity
        totals["sugar"] += food.get("sugar", 0) * quantity
        totals["sodium"] += food.get("sodium", 0) * quantity
    
    return {
        "date": date,
        "meals": daily_data.get("meals", []),
        "water_intake": daily_data.get("water_intake", 0),
        "notes": daily_data.get("notes", ""),
        "totals": totals
    }

@router.post("/{email}/nutrition/{date}/meal")
async def add_meal_entry(email: str, date: str, meal_entry: MealEntry, current_user: dict = Depends(get_current_user)):
    """Add a meal entry for a specific date - saves to top-level meals array"""
    # Ensure user can only access their own data
    if current_user["email"].lower() != email.strip().lower():
        raise HTTPException(status_code=403, detail="Not authorized to add meals for this user")
    
    db = get_db()
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Convert meal_entry to dict and add date, timestamp, and unique ID
    meal_dict = meal_entry.dict()
    meal_dict["date"] = date  # Add date to meal entry
    meal_dict["timestamp"] = datetime.utcnow().isoformat()
    meal_dict["_id"] = str(datetime.utcnow().timestamp())  # Unique ID for each meal
    meal_dict["meal_type"] = meal_entry.meal_type  # Ensure meal_type is included (breakfast, lunch, snacks, dinner)
    
    try:
        # Ensure meals array exists (for existing users who don't have it)
        if "meals" not in user:
            await db.users.update_one(
                {"_id": user["_id"]},
                {"$set": {"meals": []}}
            )
        
        # Push the meal to the top-level meals array using $push
        result = await db.users.update_one(
            {"_id": user["_id"]},
            {"$push": {"meals": meal_dict}}
        )
        
        logger.info(f"Update result - matched: {result.matched_count}, modified: {result.modified_count}")
        logger.info(f"Saving meal for user {email} on date {date}. Meal type: {meal_entry.meal_type}, Food: {meal_dict.get('food_item', {}).get('name', 'Unknown')}")
        
        # Also save to nutritionData for backward compatibility
        nutrition_data = user.get("nutritionData", {})
        if date not in nutrition_data:
            nutrition_data[date] = {
                "date": date,
                "meals": [],
                "water_intake": 0,
                "notes": ""
            }
        nutrition_data[date]["meals"].append(meal_dict)
        
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"nutritionData": nutrition_data}}
        )
        
        # Verify the data was saved by reading it back
        updated_user = await db.users.find_one({"email": email.strip().lower()})
        if updated_user:
            saved_meals = updated_user.get("meals", [])
            saved_meals_count = len(saved_meals)
            today_meals = [m for m in saved_meals if m.get("date") == date]
            logger.info(f"Verified: {saved_meals_count} total meals, {len(today_meals)} meals for date {date}")
            
            if saved_meals_count == 0:
                logger.error(f"CRITICAL: No meals found in meals array after save!")
                raise HTTPException(status_code=500, detail="Meal was not saved to database. Please try again.")
        else:
            logger.error(f"CRITICAL: User not found after update!")
            raise HTTPException(status_code=500, detail="Failed to verify meal save")
            
    except Exception as e:
        logger.error(f"Error saving meal to database: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # Count meals for today
    updated_user = await db.users.find_one({"email": email.strip().lower()})
    today_meals = [m for m in updated_user.get("meals", []) if m.get("date") == date]
    
    return {
        "message": "Meal entry added successfully", 
        "meal": meal_dict,
        "total_meals_today": len(today_meals),
        "meal_type": meal_entry.meal_type
    }

@router.patch("/{email}/nutrition/{date}/water")
async def update_water_intake(email: str, date: str, water_data: dict, current_user: dict = Depends(get_current_user)):
    """Update water intake for a specific date"""
    # Ensure user can only access their own data
    if current_user["email"].lower() != email.strip().lower():
        raise HTTPException(status_code=403, detail="Not authorized to update water intake for this user")
    
    db = get_db()
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    nutrition_data = user.get("nutritionData", {})
    if date not in nutrition_data:
        nutrition_data[date] = {
            "date": date,
            "meals": [],
            "water_intake": 0,
            "notes": ""
        }
    
    nutrition_data[date]["water_intake"] = water_data.get("water_intake", 0)
    
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"nutritionData": nutrition_data}}
    )
    
    return {"message": "Water intake updated successfully", "water_intake": nutrition_data[date]["water_intake"]}

@router.get("/{email}/nutrition/goals")
async def get_nutrition_goals(email: str, current_user: dict = Depends(get_current_user)):
    """Get user's nutrition goals"""
    # Ensure user can only access their own data
    if current_user["email"].lower() != email.strip().lower():
        raise HTTPException(status_code=403, detail="Not authorized to view nutrition goals for this user")
    
    db = get_db()
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    goals = user.get("nutritionGoals", {
        "daily_calories": 2000,
        "daily_protein": 50,
        "daily_carbs": 250,
        "daily_fat": 65,
        "daily_fiber": 25,
        "daily_water": 2000
    })
    
    return goals

@router.patch("/{email}/nutrition/goals")
async def update_nutrition_goals(email: str, goals: NutritionGoal, current_user: dict = Depends(get_current_user)):
    """Update user's nutrition goals"""
    # Ensure user can only access their own data
    if current_user["email"].lower() != email.strip().lower():
        raise HTTPException(status_code=403, detail="Not authorized to update nutrition goals for this user")
    
    db = get_db()
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"nutritionGoals": goals.dict()}}
    )
    
    return {"message": "Nutrition goals updated successfully", "goals": goals.dict()}

@router.get("/{email}/nutrition/summary")
async def get_nutrition_summary(email: str, days: int = 7, current_user: dict = Depends(get_current_user)):
    """Get nutrition summary for the last N days"""
    # Ensure user can only access their own data
    if current_user["email"].lower() != email.strip().lower():
        raise HTTPException(status_code=403, detail="Not authorized to view nutrition summary for this user")
    
    db = get_db()
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    nutrition_data = user.get("nutritionData", {})
    goals = user.get("nutritionGoals", {
        "daily_calories": 2000,
        "daily_protein": 50,
        "daily_carbs": 250,
        "daily_fat": 65,
        "daily_fiber": 25,
        "daily_water": 2000
    })
    
    # Get dates for the last N days
    today = datetime.now().date()
    dates = [(today - datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]
    
    summary = []
    for date in dates:
        daily_data = nutrition_data.get(date, {"meals": [], "water_intake": 0})
        
        totals = {
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0,
            "fiber": 0,
            "sugar": 0,
            "sodium": 0
        }
        
        for meal in daily_data.get("meals", []):
            food = meal.get("food_item", {})
            quantity = meal.get("quantity", 1)
            totals["calories"] += food.get("calories", 0) * quantity
            totals["protein"] += food.get("protein", 0) * quantity
            totals["carbs"] += food.get("carbs", 0) * quantity
            totals["fat"] += food.get("fat", 0) * quantity
            totals["fiber"] += food.get("fiber", 0) * quantity
            totals["sugar"] += food.get("sugar", 0) * quantity
            totals["sodium"] += food.get("sodium", 0) * quantity
        
        summary.append({
            "date": date,
            "totals": totals,
            "water_intake": daily_data.get("water_intake", 0),
            "goals": goals
        })
    
    return summary

# /me endpoints for authenticated users
@router.get("/me/nutrition/summary")
async def get_nutrition_summary_me(days: int = 7, current_user: dict = Depends(get_current_user)):
    """Get nutrition summary for the current authenticated user"""
    return await get_nutrition_summary(current_user["email"], days, current_user)

@router.get("/me/nutrition/verify")
async def verify_nutrition_data(current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    """Verify nutrition data is being saved correctly for the current user"""
    user = await db.users.find_one({"email": current_user["email"].lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check meals array (new structure)
    meals_array = user.get("meals", [])
    
    # Also check nutritionData for backward compatibility
    nutrition_data = user.get("nutritionData", {})
    
    # Count total meals across all dates in nutritionData
    total_meals_nutrition = 0
    meals_by_date = {}
    for date, daily_data in nutrition_data.items():
        if isinstance(daily_data, dict):
            meals = daily_data.get("meals", [])
            meal_count = len(meals) if isinstance(meals, list) else 0
            total_meals_nutrition += meal_count
            if meal_count > 0:
                meals_by_date[date] = {
                    "meal_count": meal_count,
                    "sample_meals": meals[:2] if meals else []  # First 2 meals as sample
                }
    
    # Group meals by date and meal_type from meals array
    meals_by_type = {}
    meals_by_date_new = {}
    for meal in meals_array:
        meal_type = meal.get("meal_type", "unknown")
        date = meal.get("date", "unknown")
        
        if meal_type not in meals_by_type:
            meals_by_type[meal_type] = 0
        meals_by_type[meal_type] += 1
        
        if date not in meals_by_date_new:
            meals_by_date_new[date] = {"breakfast": 0, "lunch": 0, "snacks": 0, "dinner": 0, "total": 0}
        if meal_type in meals_by_date_new[date]:
            meals_by_date_new[date][meal_type] += 1
        meals_by_date_new[date]["total"] += 1
    
    return {
        "email": current_user["email"],
        "user_id": str(user.get("_id", "")),
        "has_meals_array": "meals" in user,
        "total_meals_in_array": len(meals_array),
        "meals_by_type": meals_by_type,
        "meals_by_date": meals_by_date_new,
        "has_nutrition_data": "nutritionData" in user,
        "total_meals_in_nutrition_data": total_meals_nutrition,
        "sample_meals": meals_array[:5] if meals_array else []  # First 5 meals as sample
    }

@router.get("/me/nutrition/{date}")
async def get_daily_nutrition_me(date: str, current_user: dict = Depends(get_current_user)):
    """Get nutrition data for a specific date for the current authenticated user"""
    return await get_daily_nutrition(current_user["email"], date, current_user)

@router.post("/me/nutrition/{date}/meal")
async def add_meal_entry_me(date: str, meal_entry: MealEntry, current_user: dict = Depends(get_current_user)):
    """Add a meal entry for the current authenticated user"""
    # Ensure meals array exists for existing users
    db = get_db()
    user = await db.users.find_one({"email": current_user["email"].lower()})
    if user and "meals" not in user:
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"meals": []}}
        )
        logger.info(f"Initialized meals array for existing user: {current_user['email']}")
    
    return await add_meal_entry(current_user["email"], date, meal_entry, current_user)

@router.get("/me/meals")
async def get_user_meals(current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    """Get all meals for the current authenticated user from the meals array"""
    user = await db.users.find_one({"email": current_user["email"].lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    meals = user.get("meals", [])
    
    # Sort by date (most recent first), then by timestamp
    meals.sort(key=lambda x: (x.get("date", ""), x.get("timestamp", "")), reverse=True)
    
    return {
        "total_meals": len(meals),
        "meals": meals
    }

@router.get("/me/meals/{date}")
async def get_meals_by_date(date: str, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    """Get meals for a specific date for the current authenticated user"""
    user = await db.users.find_one({"email": current_user["email"].lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    meals = user.get("meals", [])
    date_meals = [m for m in meals if m.get("date") == date]
    
    # Group by meal_type
    meals_by_type = {
        "breakfast": [],
        "lunch": [],
        "snacks": [],
        "dinner": []
    }
    
    for meal in date_meals:
        meal_type = meal.get("meal_type", "snacks")
        if meal_type in meals_by_type:
            meals_by_type[meal_type].append(meal)
    
    return {
        "date": date,
        "total_meals": len(date_meals),
        "meals_by_type": meals_by_type,
        "all_meals": date_meals
    }

@router.patch("/me/nutrition/{date}/water")
async def update_water_intake_me(date: str, water_data: dict, current_user: dict = Depends(get_current_user)):
    """Update water intake for the current authenticated user"""
    return await update_water_intake(current_user["email"], date, water_data, current_user)

@router.patch("/me/nutrition/goals")
async def update_nutrition_goals_me(goals: NutritionGoal, current_user: dict = Depends(get_current_user)):
    """Update nutrition goals for the current authenticated user"""
    return await update_nutrition_goals(current_user["email"], goals, current_user)

@router.delete("/{email}/nutrition/{date}")
async def delete_daily_nutrition(email: str, date: str, current_user: dict = Depends(get_current_user)):
    """Delete all nutrition data for a specific date"""
    # Ensure user can only access their own data
    if current_user["email"].lower() != email.strip().lower():
        raise HTTPException(status_code=403, detail="Not authorized to delete nutrition data for this user")
    
    db = get_db()
    user = await db.users.find_one({"email": email.strip().lower()})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    nutrition_data = user.get("nutritionData", {})
    if date in nutrition_data:
        del nutrition_data[date]
        
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"nutritionData": nutrition_data}}
        )
        
        return {"message": f"Nutrition data for {date} deleted successfully"}
    else:
        return {"message": f"No nutrition data found for {date}"}