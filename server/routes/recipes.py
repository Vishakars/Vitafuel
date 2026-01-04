import logging
from fastapi import APIRouter, Depends, HTTPException
from routes.auth import get_current_user
from config.settings import get_settings
import httpx

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)


@router.get("/recipes/search")
async def search_recipes(
    ingredients: str,
    limit: int = 3,
    current_user: dict = Depends(get_current_user)
):
    """Proxy search requests to Spoonacular so API keys stay on the server."""
    api_key = settings.spoonacular_api_key
    if not api_key:
        raise HTTPException(status_code=500, detail="Recipe search service is not configured")

    normalized_limit = max(1, min(limit, 5))
    params = {
        "ingredients": ingredients,
        "number": normalized_limit,
        "apiKey": api_key
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                "https://api.spoonacular.com/recipes/findByIngredients",
                params=params
            )
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError as exc:
        logger.exception("Error fetching recipes from Spoonacular")
        raise HTTPException(status_code=502, detail="Unable to fetch recipes right now") from exc

    results = []
    for item in data:
        results.append({
            "id": item.get("id"),
            "title": item.get("title"),
            "image": item.get("image"),
            "missingIngredients": [
                ingredient.get("name")
                for ingredient in item.get("missedIngredients", [])
            ],
            "usedIngredients": [
                ingredient.get("name")
                for ingredient in item.get("usedIngredients", [])
            ]
        })

    return results

