from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone

# Import video generation service
from models.timestamp_models import Timestamp, TimestampItem
from services.video.video_generation_service import VideoGenerationService
from services.video.video_config import VideoConfig


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str


# =============================================================================
# VIDEO GENERATION MODELS
# =============================================================================

class VideoGenerationRequest(BaseModel):
    """Requête de génération de vidéo"""
    timestamp: Timestamp
    title: str = "video"
    background_music: Optional[str] = None
    weather_effect: Optional[str] = None  # 'rain', 'snow', 'fire' ou None
    use_crossfade: bool = True


class VideoGenerationResponse(BaseModel):
    """Réponse de génération de vidéo"""
    success: bool
    video_path: Optional[str] = None
    duration_seconds: Optional[float] = None
    clips_count: int = 0
    message: str


# =============================================================================
# VIDEO SERVICE INSTANCE
# =============================================================================

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialiser le service de génération vidéo
video_service = VideoGenerationService()
logger.info("Service de génération vidéo initialisé")


# =============================================================================
# ROUTES
# =============================================================================

@api_router.get("/")
async def root():
    return {
        "message": "API de Génération Vidéo",
        "version": "1.0.0",
        "endpoints": {
            "generate_video": "/api/video/generate",
            "download_video": "/api/video/download/{filename}",
            "available_effects": "/api/video/effects"
        }
    }

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks


# =============================================================================
# VIDEO GENERATION ROUTES
# =============================================================================

@api_router.post("/video/generate", response_model=VideoGenerationResponse)
async def generate_video(request: VideoGenerationRequest):
    """
    Génère une vidéo à partir d'un objet Timestamp
    
    Args:
        request: Données de la requête contenant timestamp, titre, etc.
    
    Returns:
        Informations sur la vidéo générée
    
    Example:
        ```json
        {
            "timestamp": {
                "id": "abc123",
                "idea_id": "idea456",
                "timestamps": [
                    {
                        "text": "Scène 1",
                        "image_path": "/app/ressources/images/image1.jpg",
                        "start_time_ms": 0,
                        "end_time_ms": 3000
                    }
                ],
                "total_duration_ms": 3000
            },
            "title": "Ma Vidéo",
            "weather_effect": "snow",
            "background_music": "/app/ressources/music/track.mp3"
        }
        ```
    """
    try:
        logger.info(f"Requête de génération vidéo: {request.title}")
        
        # Générer la vidéo (synchrone)
        result = video_service.generate_video(
            timestamp=request.timestamp,
            title=request.title,
            background_music=request.background_music,
            weather_effect=request.weather_effect,
            use_crossfade=request.use_crossfade
        )
        
        return VideoGenerationResponse(**result)
        
    except Exception as e:
        logger.error(f"Erreur génération vidéo: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur génération vidéo: {str(e)}")


@api_router.get("/video/download/{video_id}")
async def download_video(video_id: str):
    """
    Télécharge une vidéo générée
    
    Args:
        video_id: ID ou nom du fichier vidéo
    
    Returns:
        Fichier vidéo
    """
    try:
        # Construire le chemin du fichier
        resources_dir = os.getenv("RESOURCES_DIR", "/app/ressources")
        videos_dir = os.path.join(resources_dir, "videos")
        
        # Rechercher le fichier (recherche récursive)
        from pathlib import Path
        video_files = list(Path(videos_dir).rglob(f"*{video_id}*.mp4"))
        
        if not video_files:
            raise HTTPException(status_code=404, detail=f"Vidéo {video_id} non trouvée")
        
        video_path = str(video_files[0])
        
        if not os.path.exists(video_path):
            raise HTTPException(status_code=404, detail="Fichier vidéo introuvable")
        
        # Retourner le fichier
        return FileResponse(
            video_path,
            media_type="video/mp4",
            filename=os.path.basename(video_path)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur téléchargement vidéo: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur téléchargement: {str(e)}")


@api_router.get("/video/effects")
async def get_available_effects():
    """
    Liste les effets météo disponibles
    
    Returns:
        Liste des effets disponibles
    """
    return {
        "available_effects": ["rain", "snow", "fire"],
        "descriptions": {
            "rain": "Effet de pluie tombante",
            "snow": "Effet de neige flottante",
            "fire": "Effet de flammes/particules chaudes"
        },
        "usage": "Utiliser le paramètre 'weather_effect' dans la requête de génération"
    }


@api_router.get("/video/config")
async def get_video_config():
    """
    Récupère la configuration actuelle du service vidéo
    
    Returns:
        Configuration du service
    """
    config = video_service.config
    return {
        "resolution": config.resolution,
        "fps": config.fps,
        "codec": config.codec,
        "fade_duration": config.fade_duration,
        "crossfade_duration": config.crossfade_duration,
        "ken_burns_enabled": config.ken_burns_enabled,
        "ken_burns_zoom_factor": config.ken_burns_zoom_factor,
        "pan_enabled": config.pan_enabled,
        "pan_distance": config.pan_distance,
        "weather_effects_enabled": config.weather_effects_enabled,
        "weather_effect_intensity": config.weather_effect_intensity,
        "background_music_volume": config.background_music_volume
    }


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()