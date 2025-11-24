"""Service principal de génération de vidéos"""
import os
import logging
from typing import Optional, List
from pathlib import Path
from slugify import slugify

from moviepy.editor import (
    ImageClip, 
    concatenate_videoclips, 
    CompositeVideoClip,
    AudioFileClip
)

from .video_config import VideoConfig, DEFAULT_CONFIG
from .transitions import TransitionManager, create_crossfade_transition
from .video_effects import EffectManager
from ...models.timestamp_models import Timestamp, TimestampItem

logger = logging.getLogger(__name__)


class VideoGenerationService:
    """Service de génération de vidéos à partir de timestamps et images"""
    
    def __init__(self, config: Optional[VideoConfig] = None):
        """
        Args:
            config: Configuration personnalisée (utilise DEFAULT_CONFIG si None)
        """
        self.config = config or DEFAULT_CONFIG
        self.transition_manager = TransitionManager(
            fade_duration=self.config.fade_duration,
            zoom_factor=self.config.ken_burns_zoom_factor,
            pan_distance=self.config.pan_distance
        )
        
        # Configuration des répertoires
        self.resources_dir = os.getenv("RESOURCES_DIR", "/app/ressources")
        self.videos_dir = os.path.join(self.resources_dir, "videos")
        os.makedirs(self.videos_dir, exist_ok=True)
        
        logger.info(f"VideoGenerationService initialisé avec résolution {self.config.resolution}")
    
    def _get_video_directory(self, title: str, subdir: str = None) -> str:
        """Obtenir le répertoire pour une vidéo
        
        Args:
            title: Titre de la vidéo (sera slugifié)
            subdir: Sous-répertoire optionnel
        
        Returns:
            Chemin du répertoire créé
        """
        slug = slugify(title)
        video_dir = os.path.join(self.videos_dir, slug)
        
        if subdir:
            video_dir = os.path.join(video_dir, subdir)
        
        os.makedirs(video_dir, exist_ok=True)
        return video_dir
    
    def _create_clip_from_image(self, timestamp_item: TimestampItem) -> Optional[ImageClip]:
        """Crée un clip vidéo à partir d'un TimestampItem
        
        Args:
            timestamp_item: Item contenant le chemin de l'image et la durée
        
        Returns:
            ImageClip ou None si l'image n'existe pas
        """
        if not timestamp_item.image_path:
            logger.warning(f"Pas d'image pour le timestamp: {timestamp_item.text}")
            return None
        
        if not os.path.exists(timestamp_item.image_path):
            logger.error(f"Image introuvable: {timestamp_item.image_path}")
            return None
        
        duration = timestamp_item.get_duration_seconds()
        
        if duration <= 0:
            logger.warning(f"Durée invalide pour {timestamp_item.text}: {duration}s")
            return None
        
        try:
            # Créer le clip image
            clip = ImageClip(timestamp_item.image_path, duration=duration)
            
            # Redimensionner à la résolution cible
            clip = clip.resize(self.config.resolution)
            
            logger.info(f"Clip créé: {timestamp_item.text} - {duration:.2f}s")
            return clip
            
        except Exception as e:
            logger.error(f"Erreur création clip pour {timestamp_item.image_path}: {e}")
            return None
    
    def _apply_transitions_to_clip(self, clip: ImageClip, index: int) -> ImageClip:
        """Applique les transitions à un clip
        
        Args:
            clip: Clip à transformer
            index: Index du clip dans la séquence (pour variation)
        
        Returns:
            Clip avec transitions appliquées
        """
        # Appliquer toutes les transitions
        clip = self.transition_manager.apply_all_transitions(
            clip,
            apply_ken_burns=self.config.ken_burns_enabled,
            apply_pan=self.config.pan_enabled
        )
        
        return clip
    
    def _add_weather_effect(self, video_clip, effect_type: Optional[str] = None):
        """Ajoute un effet météo sur la vidéo
        
        Args:
            video_clip: Clip vidéo de base
            effect_type: Type d'effet ('rain', 'snow', 'fire') ou None
        
        Returns:
            Clip composite avec effet
        """
        if not effect_type or not self.config.weather_effects_enabled:
            return video_clip
        
        try:
            # Créer l'effet
            effect = EffectManager.create_effect(
                effect_type,
                self.config.width,
                self.config.height,
                self.config.weather_effect_intensity
            )
            
            # Créer l'overlay animé
            overlay = effect.create_overlay(
                duration=video_clip.duration,
                fps=self.config.fps
            )
            
            # Composer la vidéo avec l'overlay
            composite = CompositeVideoClip([video_clip, overlay])
            logger.info(f"Effet {effect_type} ajouté à la vidéo")
            
            return composite
            
        except Exception as e:
            logger.error(f"Erreur ajout effet {effect_type}: {e}")
            return video_clip
    
    def _add_background_music(self, video_clip, music_path: Optional[str] = None):
        """Ajoute une musique de fond à la vidéo
        
        Args:
            video_clip: Clip vidéo
            music_path: Chemin du fichier audio
        
        Returns:
            Clip avec audio
        """
        if not music_path or not os.path.exists(music_path):
            return video_clip
        
        try:
            # Charger l'audio
            audio = AudioFileClip(music_path)
            
            # Ajuster le volume
            audio = audio.volumex(self.config.background_music_volume)
            
            # Si l'audio est plus court, le boucler
            if audio.duration < video_clip.duration:
                num_loops = int(video_clip.duration / audio.duration) + 1
                audio = audio.loop(n=num_loops)
            
            # Couper à la durée de la vidéo
            audio = audio.subclip(0, video_clip.duration)
            
            # Ajouter l'audio à la vidéo
            video_clip = video_clip.set_audio(audio)
            logger.info(f"Musique de fond ajoutée: {music_path}")
            
            return video_clip
            
        except Exception as e:
            logger.error(f"Erreur ajout musique: {e}")
            return video_clip
    
    def generate_video(
        self,
        timestamp: Timestamp,
        output_path: Optional[str] = None,
        title: str = "video",
        background_music: Optional[str] = None,
        weather_effect: Optional[str] = None,
        use_crossfade: bool = True
    ) -> dict:
        """Génère une vidéo à partir d'un objet Timestamp
        
        Args:
            timestamp: Objet Timestamp contenant les items avec images
            output_path: Chemin de sortie (généré automatiquement si None)
            title: Titre de la vidéo (utilisé pour le nom de fichier)
            background_music: Chemin du fichier audio de fond
            weather_effect: Type d'effet météo ('rain', 'snow', 'fire') ou None
            use_crossfade: Utiliser des transitions crossfade entre clips
        
        Returns:
            Dict avec les informations de la vidéo générée
            {
                "success": bool,
                "video_path": str,
                "duration_seconds": float,
                "clips_count": int,
                "message": str
            }
        """
        logger.info("=" * 50)
        logger.info(f"Début génération vidéo: {title}")
        logger.info(f"Timestamps: {len(timestamp.timestamps)} items")
        logger.info("=" * 50)
        
        try:
            # Filtrer les items avec images valides
            valid_items = [
                item for item in timestamp.timestamps 
                if item.image_path and os.path.exists(item.image_path)
            ]
            
            if not valid_items:
                return {
                    "success": False,
                    "message": "Aucune image valide trouvée dans les timestamps",
                    "clips_count": 0
                }
            
            logger.info(f"Items valides: {len(valid_items)}/{len(timestamp.timestamps)}")
            
            # Créer les clips
            clips: List[ImageClip] = []
            for idx, item in enumerate(valid_items):
                clip = self._create_clip_from_image(item)
                if clip:
                    # Appliquer les transitions
                    clip = self._apply_transitions_to_clip(clip, idx)
                    clips.append(clip)
            
            if not clips:
                return {
                    "success": False,
                    "message": "Aucun clip valide généré",
                    "clips_count": 0
                }
            
            logger.info(f"Clips créés: {len(clips)}")
            
            # Concaténer les clips
            if use_crossfade and len(clips) > 1:
                # Utiliser crossfade entre les clips
                logger.info("Application des crossfades...")
                final_clips = [clips[0]]
                
                for i in range(1, len(clips)):
                    # Créer la transition crossfade
                    transition = create_crossfade_transition(
                        final_clips[-1],
                        clips[i],
                        self.config.crossfade_duration
                    )
                    # Remplacer les deux derniers clips par la transition
                    final_clips[-1] = transition
                    if i < len(clips) - 1:
                        final_clips.append(clips[i])
                
                final_video = concatenate_videoclips(final_clips, method="compose")
            else:
                # Concaténation simple
                final_video = concatenate_videoclips(clips, method="compose")
            
            logger.info(f"Vidéo concaténée: {final_video.duration:.2f}s")
            
            # Ajouter effet météo si demandé
            if weather_effect:
                final_video = self._add_weather_effect(final_video, weather_effect)
            
            # Ajouter musique de fond si fournie
            if background_music:
                final_video = self._add_background_music(final_video, background_music)
            
            # Générer le chemin de sortie si non fourni
            if not output_path:
                video_dir = self._get_video_directory(title)
                output_filename = f"{slugify(title)}_{timestamp.id[:8]}.mp4"
                output_path = os.path.join(video_dir, output_filename)
            
            # S'assurer que le répertoire de sortie existe
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Exporter la vidéo
            logger.info(f"Export vers: {output_path}")
            final_video.write_videofile(
                output_path,
                fps=self.config.fps,
                codec=self.config.codec,
                audio_codec=self.config.audio_codec,
                bitrate=self.config.bitrate,
                audio_bitrate=self.config.audio_bitrate,
                preset='medium',
                threads=4
            )
            
            # Nettoyer
            final_video.close()
            for clip in clips:
                clip.close()
            
            logger.info("=" * 50)
            logger.info(f"✅ Vidéo générée avec succès: {output_path}")
            logger.info(f"Durée: {final_video.duration:.2f}s")
            logger.info(f"Clips utilisés: {len(clips)}")
            logger.info("=" * 50)
            
            return {
                "success": True,
                "video_path": output_path,
                "duration_seconds": final_video.duration,
                "clips_count": len(clips),
                "message": "Vidéo générée avec succès"
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur génération vidéo: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Erreur: {str(e)}",
                "clips_count": 0
            }


# Factory function pour faciliter l'utilisation
def create_video_service(config: Optional[VideoConfig] = None) -> VideoGenerationService:
    """Crée une instance du service de génération vidéo
    
    Args:
        config: Configuration personnalisée (optionnel)
    
    Returns:
        Instance de VideoGenerationService
    """
    return VideoGenerationService(config)
