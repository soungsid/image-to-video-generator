"""Package de génération de vidéos"""
from .video_generation_service import VideoGenerationService
from .video_config import VideoConfig, DEFAULT_CONFIG
from .transitions import TransitionManager
from .video_effects import EffectManager

__all__ = [
    'VideoGenerationService',
    'VideoConfig',
    'DEFAULT_CONFIG',
    'TransitionManager',
    'EffectManager',
]
