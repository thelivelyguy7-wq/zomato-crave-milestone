from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging

from src.data.repository import RestaurantRepository
from src.services.llm.groq_client import GroqClient
from src.services.recommendation import RecommendationService
from src.config import get_settings
from src.api.schemas import (
    HealthResponse,
    LocationsResponse,
    CuisinesResponse,
    RecommendationRequest,
    RecommendationResponse
)
from fastapi.staticfiles import StaticFiles
import os

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Zomato AI Recommendation API",
    description="Backend API for AI-powered restaurant recommendations using Groq and Llama 3.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to actual frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/app", StaticFiles(directory=frontend_dir, html=True), name="frontend")


# Dependency injection for our services
repository = None
recommendation_service = None

@app.on_event("startup")
def startup_event():
    global repository, recommendation_service
    logger.info("Initializing application dependencies...")
    repository = RestaurantRepository()
    
    settings = get_settings()
    llm_client = None
    if settings.has_api_key:
        try:
            llm_client = GroqClient()
            logger.info("GroqClient initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize GroqClient: {e}")
    else:
        logger.warning("No GROQ_API_KEY found, running in degraded mode (no AI).")

    recommendation_service = RecommendationService(repository, llm_client)
    logger.info("Application startup complete.")

@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="ok", version="1.0.0")

@app.get("/locations", response_model=LocationsResponse)
def get_locations():
    if not repository:
        raise HTTPException(status_code=503, detail="Service unavailable")
    locations = repository.get_locations()
    return LocationsResponse(locations=locations)

@app.get("/cuisines", response_model=CuisinesResponse)
def get_cuisines():
    if not repository:
        raise HTTPException(status_code=503, detail="Service unavailable")
    cuisines = repository.get_cuisines()
    return CuisinesResponse(cuisines=cuisines)

@app.post("/recommendations", response_model=RecommendationResponse)
def get_recommendations(request: RecommendationRequest):
    if not recommendation_service:
        raise HTTPException(status_code=503, detail="Service unavailable")
    
    try:
        results = recommendation_service.recommend(request)
        
        # Determine if fallback was used by checking if LLM client is missing 
        # or if results have placeholder explanations
        fallback_used = False
        if not recommendation_service.llm_client:
            fallback_used = True
        elif len(results) > 0 and results[0].explanation.startswith("Matches your preferences"):
            fallback_used = True
            
        summary = "AI Recommendations based on your preferences." if not fallback_used else "Standard recommendations (AI unavailable)."
        
        return RecommendationResponse(
            summary=summary,
            fallback_used=fallback_used,
            recommendations=results
        )
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))
