"""Configuration pour la génération de vidéos"""
from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass
class VideoConfig:
    """Configuration pour la génération de vidéos"""
    
    # Paramètres de résolution
    resolution: Tuple[int, int] = (1920, 1080)  # 1080p
    fps: int = 24
    
    # Paramètres de qualité
    codec: str = 'libx264'
    audio_codec: str = 'aac'
    bitrate: str = '5000k'
    audio_bitrate: str = '192k'
    
    # Paramètres des transitions
    fade_duration: float = 0.5  # secondes
    crossfade_duration: float = 0.5  # secondes
    
    # Paramètres Ken Burns (zoom)
    ken_burns_enabled: bool = True
    ken_burns_zoom_factor: float = 1.1  # 10% de zoom
    
    # Paramètres Pan (mouvement)
    pan_enabled: bool = True
    pan_distance: int = 50  # pixels de mouvement
    
    # Effets vivants
    weather_effects_enabled: bool = True
    weather_effect_intensity: float = 0.3  # 0.0 à 1.0
    
    # Musique de fond
    background_music_volume: float = 0.3  # 30% du volume original
    
    @property
    def width(self) -> int:
        return self.resolution[0]
    
    @property
    def height(self) -> int:
        return self.resolution[1]


# Configuration par défaut
DEFAULT_CONFIG = VideoConfig()
