from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
import os
from config.settings import get_settings
from config.db import get_db
from routes.auth import router as auth_router
from routes.health import router as health_router
from routes.profile import router as profile_router
from routes.menstruation import router as menstruation_router
from routes.anemia import router as anemia_router
from routes.blood_pressure import router as bp_router
from routes.diabetes import router as diabetes_router
from routes.thyroid import router as thyroid_router
from routes.sleep_module import router as sleep_router
from routes.mental_health import router as mental_router
from routes.obesity import router as obesity_router
from routes.skin_conditions import router as skin_router
from routes.sinusitis import router as sinusitis_router
from routes.nutrition import router as nutrition_router
from routes.activity import router as activity_router
from routes.analytics import router as analytics_router
from routes.gemini import router as gemini_router
from routes.recipes import router as recipes_router

settings = get_settings()

app = FastAPI(title="VitaFuel API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static for uploads (avatars)
os.makedirs(os.path.join("uploads", "avatars"), exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/health")
async def healthcheck():
    # simple DB ping
    db = get_db()
    await db.command("ping")
    return {"status": "ok"}

# Routers will be included here
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(health_router, prefix="/api/health", tags=["health"])
app.include_router(profile_router, prefix="/api/profile", tags=["profile"])
app.include_router(menstruation_router, prefix="/api/menstruation", tags=["menstruation"])
app.include_router(anemia_router, prefix="/api/anemia", tags=["anemia"])
app.include_router(bp_router, prefix="/api/blood-pressure", tags=["blood_pressure"])
app.include_router(diabetes_router, prefix="/api/diabetes", tags=["diabetes"])
app.include_router(thyroid_router, prefix="/api/thyroid", tags=["thyroid"])
app.include_router(sleep_router, prefix="/api/sleep", tags=["sleep"])
app.include_router(mental_router, prefix="/api/mental", tags=["mental"])
app.include_router(obesity_router, prefix="/api/obesity", tags=["obesity"])
app.include_router(skin_router, prefix="/api/skin", tags=["skin"])
app.include_router(sinusitis_router, prefix="/api/sinusitis", tags=["sinusitis"])
app.include_router(nutrition_router, prefix="/api/nutrition", tags=["nutrition"])
app.include_router(activity_router, prefix="/api/activity", tags=["activity"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["analytics"])
app.include_router(recipes_router, prefix="/api", tags=["recipes"])
app.include_router(gemini_router, prefix="/api", tags=["gemini"])
