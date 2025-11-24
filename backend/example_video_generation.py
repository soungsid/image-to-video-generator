"""Exemple d'utilisation du service de génération vidéo"""
import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from models.timestamp_models import Timestamp, TimestampItem
from services.video.video_generation_service import VideoGenerationService
from services.video.video_config import VideoConfig
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def create_sample_timestamp() -> Timestamp:
    """Crée un exemple de timestamp avec des images
    
    Note: Remplacez les chemins d'images par vos propres images
    """
    # Créer des items de timestamp
    items = [
        TimestampItem(
            text="Première scène",
            image_path="/path/to/image1.jpg",  # À remplacer
            start_time_ms=0,
            end_time_ms=3000,  # 3 secondes
            confidence=0.95
        ),
        TimestampItem(
            text="Deuxième scène",
            image_path="/path/to/image2.jpg",  # À remplacer
            start_time_ms=3000,
            end_time_ms=6000,  # 3 secondes
            confidence=0.92
        ),
        TimestampItem(
            text="Troisième scène",
            image_path="/path/to/image3.jpg",  # À remplacer
            start_time_ms=6000,
            end_time_ms=10000,  # 4 secondes
            confidence=0.88
        ),
    ]
    
    # Créer le timestamp
    timestamp = Timestamp(
        idea_id="example-idea-123",
        timestamps=items,
        total_duration_ms=10000
    )
    
    return timestamp


def example_basic_video():
    """Exemple 1: Génération vidéo basique"""
    logger.info("\n" + "="*50)
    logger.info("EXEMPLE 1: Génération vidéo basique")
    logger.info("="*50 + "\n")
    
    # Créer le service
    service = VideoGenerationService()
    
    # Créer un timestamp d'exemple
    timestamp = create_sample_timestamp()
    
    # Générer la vidéo
    result = service.generate_video(
        timestamp=timestamp,
        title="Ma Première Vidéo"
    )
    
    # Afficher le résultat
    if result["success"]:
        logger.info(f"✅ Succès! Vidéo créée: {result['video_path']}")
        logger.info(f"Durée: {result['duration_seconds']:.2f}s")
        logger.info(f"Clips utilisés: {result['clips_count']}")
    else:
        logger.error(f"❌ Erreur: {result['message']}")


def example_video_with_music():
    """Exemple 2: Vidéo avec musique de fond"""
    logger.info("\n" + "="*50)
    logger.info("EXEMPLE 2: Vidéo avec musique de fond")
    logger.info("="*50 + "\n")
    
    service = VideoGenerationService()
    timestamp = create_sample_timestamp()
    
    # Générer avec musique
    result = service.generate_video(
        timestamp=timestamp,
        title="Vidéo avec Musique",
        background_music="/path/to/music.mp3"  # À remplacer
    )
    
    if result["success"]:
        logger.info(f"✅ Vidéo avec musique créée: {result['video_path']}")
    else:
        logger.error(f"❌ Erreur: {result['message']}")


def example_video_with_weather_effect():
    """Exemple 3: Vidéo avec effet météo (pluie, neige, feu)"""
    logger.info("\n" + "="*50)
    logger.info("EXEMPLE 3: Vidéo avec effets météo")
    logger.info("="*50 + "\n")
    
    service = VideoGenerationService()
    timestamp = create_sample_timestamp()
    
    # Test avec pluie
    result_rain = service.generate_video(
        timestamp=timestamp,
        title="Vidéo avec Pluie",
        weather_effect="rain"
    )
    
    if result_rain["success"]:
        logger.info(f"✅ Vidéo avec pluie: {result_rain['video_path']}")
    
    # Test avec neige
    result_snow = service.generate_video(
        timestamp=timestamp,
        title="Vidéo avec Neige",
        weather_effect="snow"
    )
    
    if result_snow["success"]:
        logger.info(f"✅ Vidéo avec neige: {result_snow['video_path']}")
    
    # Test avec feu
    result_fire = service.generate_video(
        timestamp=timestamp,
        title="Vidéo avec Feu",
        weather_effect="fire"
    )
    
    if result_fire["success"]:
        logger.info(f"✅ Vidéo avec feu: {result_fire['video_path']}")


def example_custom_config():
    """Exemple 4: Configuration personnalisée"""
    logger.info("\n" + "="*50)
    logger.info("EXEMPLE 4: Configuration personnalisée")
    logger.info("="*50 + "\n")
    
    # Créer une configuration personnalisée
    custom_config = VideoConfig(
        resolution=(1280, 720),  # 720p au lieu de 1080p
        fps=30,  # 30 fps au lieu de 24
        fade_duration=1.0,  # Fade plus long
        ken_burns_zoom_factor=1.2,  # Zoom plus prononcé
        weather_effect_intensity=0.5  # Effets plus intenses
    )
    
    # Créer le service avec la config personnalisée
    service = VideoGenerationService(config=custom_config)
    timestamp = create_sample_timestamp()
    
    result = service.generate_video(
        timestamp=timestamp,
        title="Vidéo Config Custom"
    )
    
    if result["success"]:
        logger.info(f"✅ Vidéo avec config custom: {result['video_path']}")


def example_complete():
    """Exemple 5: Vidéo complète avec tous les effets"""
    logger.info("\n" + "="*50)
    logger.info("EXEMPLE 5: Vidéo complète (musique + effet)")
    logger.info("="*50 + "\n")
    
    service = VideoGenerationService()
    timestamp = create_sample_timestamp()
    
    result = service.generate_video(
        timestamp=timestamp,
        title="Vidéo Complète",
        background_music="/path/to/music.mp3",  # À remplacer
        weather_effect="snow",
        use_crossfade=True
    )
    
    if result["success"]:
        logger.info(f"✅ Vidéo complète créée: {result['video_path']}")
        logger.info(f"Durée: {result['duration_seconds']:.2f}s")
        logger.info(f"Clips: {result['clips_count']}")


if __name__ == "__main__":
    # Décommenter les exemples que vous voulez tester
    
    logger.info("\n" + "#"*70)
    logger.info("#  EXEMPLES D'UTILISATION DU SERVICE DE GÉNÉRATION VIDÉO")
    logger.info("#"*70 + "\n")
    
    # IMPORTANT: Remplacez les chemins d'images dans create_sample_timestamp()
    # avant d'exécuter ces exemples
    
    # example_basic_video()
    # example_video_with_music()
    # example_video_with_weather_effect()
    # example_custom_config()
    # example_complete()
    
    logger.info("\n⚠️  N'oubliez pas de remplacer les chemins d'images et de musique!")
    logger.info("Modifiez la fonction create_sample_timestamp() avec vos vrais chemins.\n")
