"""Script de test pour la génération de vidéos"""
import os
import sys
from pathlib import Path
import json

# Ajouter le répertoire backend au path
sys.path.insert(0, str(Path(__file__).parent))

from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Configuration
TEST_IMAGES_DIR = "./ressources/test_images"
os.makedirs(TEST_IMAGES_DIR, exist_ok=True)


def create_test_images():
    """Crée des images de test colorées"""
    print("🎨 Création des images de test...")
    
    colors = [
        ((255, 100, 100), "Image 1 - Rouge"),
        ((100, 255, 100), "Image 2 - Vert"),
        ((100, 100, 255), "Image 3 - Bleu"),
        ((255, 255, 100), "Image 4 - Jaune"),
        ((255, 100, 255), "Image 5 - Magenta"),
    ]
    
    image_paths = []
    
    for idx, (color, text) in enumerate(colors, 1):
        # Créer une image
        img = Image.new('RGB', (1920, 1080), color=color)
        draw = ImageDraw.Draw(img)
        
        # Ajouter du texte
        try:
            # Essayer d'utiliser une police par défaut
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        except:
            font = ImageFont.load_default()
        
        # Dessiner le texte au centre
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((1920 - text_width) // 2, (1080 - text_height) // 2)
        
        draw.text(position, text, fill=(255, 255, 255), font=font)
        
        # Ajouter des formes décoratives
        for i in range(10):
            x = np.random.randint(0, 1920)
            y = np.random.randint(0, 1080)
            size = np.random.randint(20, 100)
            draw.ellipse([x, y, x+size, y+size], fill=(255, 255, 255, 128))
        
        # Sauvegarder
        image_path = os.path.join(TEST_IMAGES_DIR, f"test_image_{idx}.jpg")
        img.save(image_path, quality=95)
        image_paths.append(image_path)
        print(f"  ✅ Créée: {image_path}")
    
    return image_paths


def test_video_generation_api():
    """Test de l'API de génération vidéo"""
    import requests
    
    print("\n" + "="*70)
    print("🎬 TEST DE L'API DE GÉNÉRATION VIDÉO")
    print("="*70 + "\n")
    
    # Créer les images de test
    image_paths = create_test_images()
    
    # Créer le payload
    timestamp_items = []
    current_time = 0
    
    for idx, image_path in enumerate(image_paths, 1):
        duration_ms = 3000  # 3 secondes par image
        timestamp_items.append({
            "text": f"Scène {idx}",
            "image_path": image_path,
            "start_time_ms": current_time,
            "end_time_ms": current_time + duration_ms,
            "confidence": 0.95
        })
        current_time += duration_ms
    
    payload = {
        "timestamp": {
            "id": "test-video-001",
            "idea_id": "test-idea-001",
            "timestamps": timestamp_items,
            "total_duration_ms": current_time
        },
        "title": "Vidéo de Test Complète",
        "use_crossfade": True
    }
    
    print("📤 Envoi de la requête à l'API...")
    print(f"Nombre d'images: {len(image_paths)}")
    print(f"Durée totale: {current_time/1000:.1f}s\n")
    
    # Appeler l'API
    try:
        response = requests.post(
            "http://localhost:8001/api/video/generate",
            json=payload,
            timeout=180  # 3 minutes max
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCÈS!")
            print(f"\n📹 Vidéo générée:")
            print(f"   Chemin: {result.get('video_path')}")
            print(f"   Durée: {result.get('duration_seconds', 0):.2f}s")
            print(f"   Clips: {result.get('clips_count', 0)}")
            print(f"   Message: {result.get('message')}")
            
            # Vérifier si le fichier existe
            video_path = result.get('video_path')
            if video_path and os.path.exists(video_path):
                size_mb = os.path.getsize(video_path) / (1024 * 1024)
                print(f"   Taille: {size_mb:.2f} MB")
                print(f"\n🎉 Fichier vidéo créé avec succès!")
            else:
                print(f"\n⚠️  Fichier vidéo non trouvé à: {video_path}")
            
            return result
        else:
            print(f"❌ ERREUR HTTP {response.status_code}")
            print(f"Détails: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_with_weather_effects():
    """Test avec effets météo"""
    import requests
    
    print("\n" + "="*70)
    print("🌨️  TEST AVEC EFFETS MÉTÉO")
    print("="*70 + "\n")
    
    image_paths = create_test_images()
    
    effects = ["rain", "snow", "fire"]
    
    for effect in effects:
        print(f"\n🎬 Test avec effet: {effect.upper()}")
        
        timestamp_items = []
        current_time = 0
        
        # Utiliser seulement 3 images pour aller plus vite
        for idx, image_path in enumerate(image_paths[:3], 1):
            duration_ms = 2000  # 2 secondes
            timestamp_items.append({
                "text": f"Scène {idx}",
                "image_path": image_path,
                "start_time_ms": current_time,
                "end_time_ms": current_time + duration_ms,
                "confidence": 0.95
            })
            current_time += duration_ms
        
        payload = {
            "timestamp": {
                "id": f"test-{effect}-001",
                "idea_id": f"test-{effect}",
                "timestamps": timestamp_items,
                "total_duration_ms": current_time
            },
            "title": f"Test {effect.capitalize()}",
            "weather_effect": effect,
            "use_crossfade": True
        }
        
        try:
            response = requests.post(
                "http://localhost:8001/api/video/generate",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ Vidéo avec {effect}: {result.get('video_path')}")
            else:
                print(f"  ❌ Erreur: {response.text}")
                
        except Exception as e:
            print(f"  ❌ Exception: {e}")


def main():
    """Fonction principale"""
    print("\n" + "#"*70)
    print("#  SUITE DE TESTS - SERVICE DE GÉNÉRATION VIDÉO")
    print("#"*70 + "\n")
    
    # Test 1: Génération basique
    result1 = test_video_generation_api()
    
    # Test 2: Avec effets météo (optionnel, commenter si trop long)
    test_with_weather_effects()
    
    print("\n" + "="*70)
    print("✅ TESTS TERMINÉS")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
