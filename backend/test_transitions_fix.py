#!/usr/bin/env python3
"""Test pour vérifier que les transitions fonctionnent après la correction"""

import os
import sys
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Ajouter le répertoire backend au path
sys.path.insert(0, str(Path(__file__).parent))

from services.video.video_generation_service import VideoGenerationService
from models.timestamp_models import Timestamp, TimestampItem

def test_transitions():
    """Test que les transitions sont appliquées"""
    print("🎬 TEST DES TRANSITIONS")
    print("=" * 50)
    
    # Créer le service
    service = VideoGenerationService()
    
    # Afficher la configuration
    print(f"Configuration actuelle:")
    print(f"  - Ken Burns activé: {service.config.ken_burns_enabled}")
    print(f"  - Pan activé: {service.config.pan_enabled}")
    print(f"  - Durée fade: {service.config.fade_duration}s")
    print(f"  - Facteur zoom: {service.config.ken_burns_zoom_factor}")
    print(f"  - Distance pan: {service.config.pan_distance}px")
    
    # Créer un timestamp avec 2 images pour voir les transitions
    timestamp_items = []
    for i in range(2):
        item = TimestampItem(
            text=f'Image test {i+1}',
            image_path=f'../ressources/test_images/test_image_{i+1}.jpg',
            start_time_ms=i * 3000,
            end_time_ms=(i + 1) * 3000,
            confidence=0.95
        )
        timestamp_items.append(item)
    
    timestamp = Timestamp(
        id='test-transitions-fix',
        idea_id='test-transitions',
        timestamps=timestamp_items,
        total_duration_ms=6000
    )
    
    print(f"\nGénération vidéo avec {len(timestamp_items)} images...")
    
    # Générer la vidéo
    result = service.generate_video(
        timestamp=timestamp,
        title='Test Transitions Fix',
        use_crossfade=True
    )
    
    print(f"\nRÉSULTAT:")
    print(f"  - Succès: {result['success']}")
    print(f"  - Message: {result['message']}")
    print(f"  - Chemin: {result.get('video_path', 'N/A')}")
    print(f"  - Durée: {result.get('duration_seconds', 0):.2f}s")
    print(f"  - Clips: {result.get('clips_count', 0)}")
    
    if result['success'] and result.get('video_path'):
        video_path = result['video_path']
        if os.path.exists(video_path):
            size_mb = os.path.getsize(video_path) / (1024 * 1024)
            print(f"  - Taille: {size_mb:.2f} MB")
            print(f"\n✅ VIDÉO CRÉÉE AVEC SUCCÈS!")
            print(f"   Fichier: {video_path}")
        else:
            print(f"\n⚠️  Fichier vidéo non trouvé: {video_path}")
    else:
        print(f"\n❌ ÉCHEC DE LA GÉNÉRATION")
    
    print("=" * 50)

def test_weather_effects():
    """Test des effets météo"""
    print("\n🌨️  TEST DES EFFETS MÉTÉO")
    print("=" * 50)
    
    service = VideoGenerationService()
    
    # Test avec effet neige
    timestamp_items = [
        TimestampItem(
            text='Test effet neige',
            image_path='../ressources/test_images/test_image_1.jpg',
            start_time_ms=0,
            end_time_ms=3000,
            confidence=0.95
        )
    ]
    
    timestamp = Timestamp(
        id='test-snow-effect',
        idea_id='test-effects',
        timestamps=timestamp_items,
        total_duration_ms=3000
    )
    
    print("Génération vidéo avec effet neige...")
    result = service.generate_video(
        timestamp=timestamp,
        title='Test Effet Neige',
        weather_effect='snow'
    )
    
    print(f"Résultat effet neige: {result['success']}")
    if result['success']:
        print(f"✅ Effet neige appliqué avec succès!")
    else:
        print(f"❌ Échec effet neige: {result['message']}")
    
    print("=" * 50)

if __name__ == "__main__":
    print("🚀 DÉBUT DES TESTS - CORRECTION TRANSITIONS")
    print()
    
    # Test des transitions
    test_transitions()
    
    # Test des effets météo
    test_weather_effects()
    
    print("\n🎉 TESTS TERMINÉS")
