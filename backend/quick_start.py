#!/usr/bin/env python3
"""
🚀 QUICK START - Service de Génération Vidéo

Ce script montre comment utiliser le service de manière simple.
Parfait pour débuter!
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire backend au path
sys.path.insert(0, str(Path(__file__).parent))

from models.timestamp_models import Timestamp, TimestampItem
from services.video.video_generation_service import VideoGenerationService
from services.video.video_config import VideoConfig
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def exemple_basique():
    """
    EXEMPLE 1: Génération vidéo basique
    
    Crée une vidéo simple à partir de 3 images
    """
    print("\n" + "="*70)
    print("📹 EXEMPLE 1: Génération Vidéo Basique")
    print("="*70 + "\n")
    
    # Étape 1: Créer le service
    service = VideoGenerationService()
    
    # Étape 2: Définir vos images et durées
    images = [
        {
            "path": "/app/ressources/test_images/test_image_1.jpg",
            "text": "Introduction",
            "duration_seconds": 3
        },
        {
            "path": "/app/ressources/test_images/test_image_2.jpg", 
            "text": "Contenu Principal",
            "duration_seconds": 4
        },
        {
            "path": "/app/ressources/test_images/test_image_3.jpg",
            "text": "Conclusion",
            "duration_seconds": 3
        }
    ]
    
    # Étape 3: Créer les TimestampItems
    timestamp_items = []
    current_time_ms = 0
    
    for img in images:
        duration_ms = int(img["duration_seconds"] * 1000)
        
        item = TimestampItem(
            text=img["text"],
            image_path=img["path"],
            start_time_ms=current_time_ms,
            end_time_ms=current_time_ms + duration_ms
        )
        
        timestamp_items.append(item)
        current_time_ms += duration_ms
    
    # Étape 4: Créer l'objet Timestamp
    timestamp = Timestamp(
        idea_id="quick-start-001",
        timestamps=timestamp_items,
        total_duration_ms=current_time_ms
    )
    
    # Étape 5: Générer la vidéo!
    result = service.generate_video(
        timestamp=timestamp,
        title="Ma Première Vidéo"
    )
    
    # Étape 6: Vérifier le résultat
    if result["success"]:
        print("✅ SUCCÈS!")
        print(f"📹 Vidéo: {result['video_path']}")
        print(f"⏱️  Durée: {result['duration_seconds']:.1f}s")
        print(f"🎬 Clips: {result['clips_count']}")
        
        # Afficher la taille du fichier
        if os.path.exists(result['video_path']):
            size_mb = os.path.getsize(result['video_path']) / (1024 * 1024)
            print(f"💾 Taille: {size_mb:.2f} MB")
    else:
        print(f"❌ ERREUR: {result['message']}")


def exemple_avec_effet():
    """
    EXEMPLE 2: Vidéo avec effet météo (neige)
    """
    print("\n" + "="*70)
    print("❄️  EXEMPLE 2: Vidéo avec Effet Neige")
    print("="*70 + "\n")
    
    service = VideoGenerationService()
    
    # 2 images simples
    timestamp_items = [
        TimestampItem(
            text="Scène hivernale 1",
            image_path="/app/ressources/test_images/test_image_1.jpg",
            start_time_ms=0,
            end_time_ms=3000
        ),
        TimestampItem(
            text="Scène hivernale 2",
            image_path="/app/ressources/test_images/test_image_2.jpg",
            start_time_ms=3000,
            end_time_ms=6000
        )
    ]
    
    timestamp = Timestamp(
        idea_id="winter-scene",
        timestamps=timestamp_items,
        total_duration_ms=6000
    )
    
    # Générer avec effet neige
    result = service.generate_video(
        timestamp=timestamp,
        title="Scène Hivernale",
        weather_effect="snow"  # 🌨️ Ajout de l'effet neige
    )
    
    if result["success"]:
        print(f"✅ Vidéo avec neige créée: {result['video_path']}")
    else:
        print(f"❌ Erreur: {result['message']}")


def exemple_personnalise():
    """
    EXEMPLE 3: Configuration personnalisée (720p, 30fps)
    """
    print("\n" + "="*70)
    print("⚙️  EXEMPLE 3: Configuration Personnalisée")
    print("="*70 + "\n")
    
    # Créer une configuration personnalisée
    custom_config = VideoConfig(
        resolution=(1280, 720),  # 720p au lieu de 1080p
        fps=30,                  # 30 fps au lieu de 24
        bitrate='3000k',         # Bitrate réduit
        weather_effect_intensity=0.5  # Effets plus intenses
    )
    
    # Créer le service avec la config custom
    service = VideoGenerationService(config=custom_config)
    
    timestamp_items = [
        TimestampItem(
            text="Test 720p",
            image_path="/app/ressources/test_images/test_image_1.jpg",
            start_time_ms=0,
            end_time_ms=3000
        )
    ]
    
    timestamp = Timestamp(
        idea_id="custom-config",
        timestamps=timestamp_items,
        total_duration_ms=3000
    )
    
    result = service.generate_video(
        timestamp=timestamp,
        title="Vidéo 720p"
    )
    
    if result["success"]:
        print(f"✅ Vidéo 720p@30fps créée: {result['video_path']}")


def exemple_complet():
    """
    EXEMPLE 4: Vidéo complète avec musique et effet
    
    NOTE: Remplacez le chemin de la musique par un vrai fichier!
    """
    print("\n" + "="*70)
    print("🎵 EXEMPLE 4: Vidéo Complète (avec musique)")
    print("="*70 + "\n")
    
    service = VideoGenerationService()
    
    timestamp_items = [
        TimestampItem(
            text="Intro",
            image_path="/app/ressources/test_images/test_image_1.jpg",
            start_time_ms=0,
            end_time_ms=3000
        ),
        TimestampItem(
            text="Milieu",
            image_path="/app/ressources/test_images/test_image_2.jpg",
            start_time_ms=3000,
            end_time_ms=6000
        ),
        TimestampItem(
            text="Fin",
            image_path="/app/ressources/test_images/test_image_3.jpg",
            start_time_ms=6000,
            end_time_ms=9000
        )
    ]
    
    timestamp = Timestamp(
        idea_id="complete-video",
        timestamps=timestamp_items,
        total_duration_ms=9000
    )
    
    # Chemin vers votre musique (si vous en avez une)
    music_path = "/app/ressources/music/background.mp3"
    
    # Vérifier si la musique existe
    if not os.path.exists(music_path):
        print(f"⚠️  Musique non trouvée: {music_path}")
        print("   Génération sans musique...\n")
        music_path = None
    
    result = service.generate_video(
        timestamp=timestamp,
        title="Vidéo Complète",
        weather_effect="rain",  # 🌧️ Effet pluie
        background_music=music_path
    )
    
    if result["success"]:
        print(f"✅ Vidéo complète créée: {result['video_path']}")


def main():
    """Fonction principale - Lance les exemples"""
    
    print("\n" + "#"*70)
    print("#  🚀 QUICK START - SERVICE DE GÉNÉRATION VIDÉO")
    print("#"*70)
    
    print("\n💡 Ce script va créer plusieurs vidéos de démonstration.")
    print("   Les vidéos seront sauvegardées dans /app/ressources/videos/\n")
    
    try:
        # Exemple 1: Basique
        exemple_basique()
        
        # Exemple 2: Avec effet
        exemple_avec_effet()
        
        # Exemple 3: Config personnalisée
        exemple_personnalise()
        
        # Exemple 4: Complet
        # exemple_complet()  # Décommentez si vous avez une musique
        
        print("\n" + "="*70)
        print("✅ TOUS LES EXEMPLES TERMINÉS!")
        print("="*70)
        
        print("\n📁 Vos vidéos sont dans: /app/ressources/videos/")
        print("\n💡 Prochaines étapes:")
        print("   1. Ouvrez les vidéos pour les voir")
        print("   2. Modifiez ce script pour tester vos propres images")
        print("   3. Consultez VIDEO_SERVICE_README.md pour plus d'infos")
        
    except Exception as e:
        logger.error(f"❌ Erreur: {e}", exc_info=True)


if __name__ == "__main__":
    main()
