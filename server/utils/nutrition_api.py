"""
Nutrition API Integration Module
Integrates with USDA FoodData Central API for comprehensive nutrition data
"""

import httpx
import os
from typing import Dict, List, Optional
import logging

from config.settings import get_settings

logger = logging.getLogger(__name__)

# USDA FoodData Central API
# You can get a free API key from: https://fdc.nal.usda.gov/api-key-signup.html
settings = get_settings()
USDA_API_KEY = settings.usda_api_key or os.getenv("USDA_API_KEY") or "DEMO_KEY"
USDA_BASE_URL = "https://api.nal.usda.gov/fdc/v1"

async def search_usda_food(query: str, limit: int = 5) -> List[Dict]:
    """
    Search for food items in USDA FoodData Central database
    
    Args:
        query: Search term (food name)
        limit: Maximum number of results to return
        
    Returns:
        List of food items with nutrition data
    """
    try:
        url = f"{USDA_BASE_URL}/foods/search"
        params = {
            "api_key": USDA_API_KEY,
            "query": query,
            "pageSize": limit,
            "dataType": ["Foundation", "SR Legacy"],  # Focus on reliable data sources
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            foods = []
            if "foods" in data:
                for food_item in data["foods"]:
                    parsed_food = parse_usda_food(food_item)
                    if parsed_food:
                        foods.append(parsed_food)
            
            return foods
            
    except httpx.TimeoutException:
        logger.error(f"Timeout while searching USDA API for: {query}")
        return []
    except httpx.HTTPError as e:
        logger.error(f"HTTP error while searching USDA API: {e}")
        return []
    except Exception as e:
        logger.error(f"Error searching USDA API: {e}")
        return []


def parse_usda_food(food_data: Dict) -> Optional[Dict]:
    """
    Parse USDA food data into our standard format
    
    Args:
        food_data: Raw food data from USDA API
        
    Returns:
        Standardized food item dictionary
    """
    try:
        # Extract basic information
        name = food_data.get("description", "Unknown Food")
        brand = food_data.get("brandOwner", None)
        
        # Initialize nutrition values
        nutrition = {
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0,
            "fiber": 0,
            "sugar": 0,
            "sodium": 0
        }
        
        # Parse nutrients
        nutrients = food_data.get("foodNutrients", [])
        for nutrient in nutrients:
            nutrient_name = nutrient.get("nutrientName", "").lower()
            nutrient_value = nutrient.get("value", 0)
            
            # Map USDA nutrient names to our format
            if "energy" in nutrient_name or "calor" in nutrient_name:
                # Convert kJ to kcal if needed
                if "kj" in nutrient_name.lower():
                    nutrition["calories"] = round(nutrient_value * 0.239, 1)
                else:
                    nutrition["calories"] = round(nutrient_value, 1)
            elif "protein" in nutrient_name:
                nutrition["protein"] = round(nutrient_value, 1)
            elif "carbohydrate" in nutrient_name and "by difference" in nutrient_name:
                nutrition["carbs"] = round(nutrient_value, 1)
            elif "total lipid" in nutrient_name or "fat, total" in nutrient_name:
                nutrition["fat"] = round(nutrient_value, 1)
            elif "fiber" in nutrient_name and "total dietary" in nutrient_name:
                nutrition["fiber"] = round(nutrient_value, 1)
            elif "sugars, total" in nutrient_name:
                nutrition["sugar"] = round(nutrient_value, 1)
            elif "sodium" in nutrient_name:
                nutrition["sodium"] = round(nutrient_value, 1)
        
        # Only return if we have at least calories or macros
        if nutrition["calories"] > 0 or nutrition["protein"] > 0:
            return {
                "name": name,
                "calories": nutrition["calories"],
                "protein": nutrition["protein"],
                "carbs": nutrition["carbs"],
                "fat": nutrition["fat"],
                "fiber": nutrition["fiber"],
                "sugar": nutrition["sugar"],
                "sodium": nutrition["sodium"],
                "serving_size": "100g",
                "brand": brand,
                "source": "USDA"
            }
        
        return None
        
    except Exception as e:
        logger.error(f"Error parsing USDA food data: {e}")
        return None


async def search_nutrition_online(query: str, limit: int = 5) -> List[Dict]:
    """
    Search for nutrition data from online sources
    Currently uses USDA FoodData Central, but can be extended to include other APIs
    
    Args:
        query: Food item to search for
        limit: Maximum number of results
        
    Returns:
        List of food items with nutrition data
    """
    # Search USDA database
    usda_results = await search_usda_food(query, limit)
    
    # Future: Can add more APIs here (Nutritionix, Edamam, etc.)
    # For now, just return USDA results
    
    return usda_results


# Alternative: Nutritionix API (requires API key)
# Uncomment and configure if you want to use Nutritionix instead
"""
NUTRITIONIX_APP_ID = os.getenv("NUTRITIONIX_APP_ID", "")
NUTRITIONIX_API_KEY = os.getenv("NUTRITIONIX_API_KEY", "")

async def search_nutritionix_food(query: str, limit: int = 5) -> List[Dict]:
    try:
        url = "https://trackapi.nutritionix.com/v2/search/instant"
        headers = {
            "x-app-id": NUTRITIONIX_APP_ID,
            "x-app-key": NUTRITIONIX_API_KEY
        }
        params = {"query": query}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            foods = []
            # Parse common foods
            for food in data.get("common", [])[:limit]:
                foods.append({
                    "name": food.get("food_name", ""),
                    "calories": food.get("full_nutrients", {}).get("208", 0),
                    "protein": food.get("full_nutrients", {}).get("203", 0),
                    "carbs": food.get("full_nutrients", {}).get("205", 0),
                    "fat": food.get("full_nutrients", {}).get("204", 0),
                    "fiber": 0,
                    "sugar": 0,
                    "sodium": 0,
                    "serving_size": "100g",
                    "brand": None,
                    "source": "Nutritionix"
                })
            
            return foods
    except Exception as e:
        logger.error(f"Error searching Nutritionix API: {e}")
        return []
"""

