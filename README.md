# 🎬 Service de Génération Vidéo Professionnel

## 📋 Description

Service Python complet et production-ready pour générer des vidéos professionnelles à partir d'images et de timestamps. Construit avec une architecture propre (SOLID, Clean Architecture) utilisant FastAPI et MoviePy.

## ✨ Fonctionnalités Principales

### 🎥 Génération Vidéo
- Concaténation automatique d'images selon durées calculées
- Résolution 1080p (configurable)
- Export MP4 (H.264/AAC)
- 24 FPS (configurable)

### 🎨 Effets Visuels
- **Pluie**: Gouttes animées tombantes
- **Neige**: Flocons flottants
- **Feu**: Flammes et particules chaudes
- Intensité configurable

### 🎵 Audio
- Musique de fond avec loop automatique
- Volume ajustable
- Support MP3, WAV, etc.

## 🚀 Démarrage Rapide

### Installation

```bash
cd /app/backend
pip install -r requirements.txt
```

### Démarrer le Serveur

```bash
sudo supervisorctl restart backend
```

### Tester le Service

```bash
cd /app/backend
python3 test_video_generation.py
```

## 📡 API Endpoints

### Génération de Vidéo

**POST** `/api/video/generate`

```json
{
  "timestamp": {
    "id": "video-001",
    "idea_id": "idea-123",
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

### Autres Endpoints

- `GET /api/video/effects` - Liste des effets disponibles
- `GET /api/video/config` - Configuration actuelle
- `GET /api/video/download/{video_id}` - Télécharger une vidéo

## 📂 Structure du Projet

```
/app/backend/
├── models/
│   └── timestamp_models.py       # Models Timestamp & TimestampItem
├── services/
│   └── video/
│       ├── video_generation_service.py  # Service principal
│       ├── video_config.py              # Configuration
│       ├── transitions.py               # Transitions
│       └── video_effects.py             # Effets vivants
├── server.py                     # API FastAPI
├── example_video_generation.py   # Exemples
├── test_video_generation.py      # Tests
└── VIDEO_SERVICE_README.md       # Documentation complète
```

## 📖 Documentation Complète

Voir **[VIDEO_SERVICE_README.md](./backend/VIDEO_SERVICE_README.md)** pour:
- Guide d'utilisation détaillé
- Exemples de code
- Configuration avancée
- Troubleshooting
- Architecture technique

## 🎓 Exemple d'Utilisation Python

```python
from services.video.video_generation_service import VideoGenerationService
from models.timestamp_models import Timestamp, TimestampItem

# Créer le service
service = VideoGenerationService()

# Créer un timestamp
timestamp = Timestamp(
    idea_id="my-idea",
    timestamps=[
        TimestampItem(
            text="Scène 1",
            image_path="/path/to/image.jpg",
            start_time_ms=0,
            end_time_ms=3000
        )
    ],
    total_duration_ms=3000
)

# Générer la vidéo
result = service.generate_video(
    timestamp=timestamp,
    title="Ma Vidéo",
    weather_effect="snow"
)

print(f"✅ Vidéo créée: {result['video_path']}")
```

## ⚙️ Configuration

```python
from services.video.video_config import VideoConfig

config = VideoConfig(
    resolution=(1920, 1080),  # 1080p
    fps=24,
    weather_effect_intensity=0.5,
    background_music_volume=0.3
)

service = VideoGenerationService(config=config)
```

## 🧪 Tests

```bash
# Test automatisé
cd /app/backend
python3 test_video_generation.py

# Test API
curl http://localhost:8001/api/video/effects
curl http://localhost:8001/api/video/config
```

## 📦 Technologies

- **FastAPI** - API REST moderne
- **MoviePy 2.x** - Traitement vidéo
- **Pillow** - Manipulation d'images
- **NumPy** - Calculs numériques
- **MongoDB** - Base de données (Motor)

## 🏗️ Architecture

- **SOLID Principles** appliqués
- **Clean Architecture** - Services découplés
- **Type Hints** complets
- **Logging** détaillé
- **Error Handling** robuste

## 📊 Performance

- **5 images (15s)**: ~10-15 secondes
- **10 images (30s)**: ~20-30 secondes
- **Taille fichier (15s, 1080p)**: ~300 KB

## 🐛 Troubleshooting

### Logs Backend
```bash
tail -f /var/log/supervisor/backend.err.log
```

### Redémarrer le Service
```bash
sudo supervisorctl restart backend
```

## 📝 Notes Importantes

- Les chemins d'images doivent être **absolus**
- Le répertoire de ressources est configurable via `RESOURCES_DIR`
- Les vidéos sont sauvegardées dans `$RESOURCES_DIR/videos/{slug}/`

## 🚀 Prochaines Étapes

Le service de base fonctionne! Les transitions avancées (fade, crossfade, Ken Burns, pan) seront réimplémentées avec la nouvelle API MoviePy 2.x dans une prochaine version.

## 📄 Licence

Code fourni comme exemple d'implémentation.
