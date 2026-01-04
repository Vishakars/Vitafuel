from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from routes.auth import get_current_user
import google.generativeai as genai
from config.settings import get_settings
import logging

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)


class ChatMessage(BaseModel):
    message: str


def get_gemini_model():
    api_key = settings.gemini_api_key
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API key is not configured")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-pro')


@router.post("/gemini")
async def chat_with_gemini(
    chat_message: ChatMessage,
    current_user: dict = Depends(get_current_user)
):
    """Chat with Gemini AI for health-related queries"""
    try:
        model = get_gemini_model()
        
        health_prompt = f"""
        You are VitaBot, a friendly and knowledgeable health assistant for the VitaFuel app. 
        You help users with health tips, nutrition advice, exercise recommendations, and general wellness guidance.
        
        User's question: {chat_message.message}
        
        Please provide a helpful, accurate, and encouraging response. Keep it conversational and include relevant emojis.
        If the question is about medical symptoms or serious health concerns, remind the user to consult a healthcare professional.
        """
        
        response = model.generate_content(health_prompt)
        
        return {
            "reply": response.text,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Gemini API error: %s", e)
        return {
            "reply": "I'm here to help with health tips, nutrition advice, and wellness guidance! 🌟 What would you like to know about?",
            "status": "fallback"
        }
