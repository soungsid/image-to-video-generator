"""Gestion des transitions pour les clips vidéo"""
import random
from typing import Tuple
from moviepy import VideoClip, CompositeVideoClip
import numpy as np
import logging

logger = logging.getLogger(__name__)


class TransitionManager:
    """Gère l'application des transitions sur les clips vidéo"""
    
    def __init__(self, fade_duration: float = 0.5, zoom_factor: float = 1.1, pan_distance: int = 50):
        """
        Args:
            fade_duration: Durée du fade en secondes
            zoom_factor: Facteur de zoom pour l'effet Ken Burns
            pan_distance: Distance de mouvement pour l'effet pan (pixels)
        """
        self.fade_duration = fade_duration
        self.zoom_factor = zoom_factor
        self.pan_distance = pan_distance
    
    def apply_fade_in(self, clip: VideoClip) -> VideoClip:
        """Applique un fade-in au début du clip"""
        # Pour MoviePy 2.x, on applique un fade simple via composition
        if clip.duration > self.fade_duration:
            # Créer un clip avec opacité variable
            def make_frame(t):
                frame = clip.get_frame(t)
                opacity = min(1.0, t / self.fade_duration) if t < self.fade_duration else 1.0
                # Appliquer l'opacité au frame
                return (frame * opacity).astype(frame.dtype)
            
            return VideoClip(make_frame, duration=clip.duration).with_fps(clip.fps)
        return clip
    
    def apply_fade_out(self, clip: VideoClip) -> VideoClip:
        """Applique un fade-out à la fin du clip"""
        if clip.duration > self.fade_duration:
            fade_start = clip.duration - self.fade_duration
            def make_frame(t):
                frame = clip.get_frame(t)
                opacity = 1.0 if t < fade_start else max(0.0, (clip.duration - t) / self.fade_duration)
                return (frame * opacity).astype(frame.dtype)
            
            return VideoClip(make_frame, duration=clip.duration).with_fps(clip.fps)
        return clip
    
    def apply_ken_burns(self, clip: VideoClip, zoom_in: bool = True) -> VideoClip:
        """Applique l'effet Ken Burns (zoom progressif)
        
        Args:
            clip: Le clip vidéo
            zoom_in: Si True, zoom avant, sinon zoom arrière
        """
        duration = clip.duration
        
        if zoom_in:
            # Zoom avant (1.0 -> zoom_factor)
            def make_frame(t):
                progress = t / duration
                current_zoom = 1.0 + (self.zoom_factor - 1.0) * progress
                frame = clip.get_frame(t)
                h, w = frame.shape[:2]
                
                # Calculer le nouveau centre
                new_w = int(w * current_zoom)
                new_h = int(h * current_zoom)
                
                # Redimensionner
                from PIL import Image
                img = Image.fromarray(frame)
                img_resized = img.resize((new_w, new_h), Image.LANCZOS)
                
                # Crop au centre
                left = (new_w - w) // 2
                top = (new_h - h) // 2
                img_cropped = img_resized.crop((left, top, left + w, top + h))
                
                return np.array(img_cropped)
        else:
            # Zoom arrière (zoom_factor -> 1.0)
            def make_frame(t):
                progress = t / duration
                current_zoom = self.zoom_factor - (self.zoom_factor - 1.0) * progress
                frame = clip.get_frame(t)
                h, w = frame.shape[:2]
                
                # Calculer le nouveau centre
                new_w = int(w * current_zoom)
                new_h = int(h * current_zoom)
                
                # Redimensionner
                from PIL import Image
                img = Image.fromarray(frame)
                img_resized = img.resize((new_w, new_h), Image.LANCZOS)
                
                # Crop au centre
                left = (new_w - w) // 2
                top = (new_h - h) // 2
                img_cropped = img_resized.crop((left, top, left + w, top + h))
                
                return np.array(img_cropped)
        
        return VideoClip(make_frame, duration=duration).with_fps(clip.fps)
    
    def apply_pan(self, clip: VideoClip, direction: str = 'random') -> VideoClip:
        """Applique un mouvement panoramique
        
        Args:
            clip: Le clip vidéo
            direction: 'left', 'right', 'up', 'down', ou 'random'
        """
        if direction == 'random':
            direction = random.choice(['left', 'right', 'up', 'down'])
        
        duration = clip.duration
        original_size = clip.size
        w, h = original_size
        
        def make_frame(t):
            progress = t / duration
            frame = clip.get_frame(t)
            
            # Calculer le décalage
            if direction == 'left':
                offset_x = int(-self.pan_distance * progress)
                offset_y = 0
            elif direction == 'right':
                offset_x = int(self.pan_distance * progress)
                offset_y = 0
            elif direction == 'up':
                offset_x = 0
                offset_y = int(-self.pan_distance * progress)
            else:  # down
                offset_x = 0
                offset_y = int(self.pan_distance * progress)
            
            # Créer une image plus grande
            from PIL import Image
            img = Image.fromarray(frame)
            expanded_w = w + abs(self.pan_distance)
            expanded_h = h + abs(self.pan_distance)
            expanded = img.resize((expanded_w, expanded_h), Image.LANCZOS)
            
            # Crop avec décalage
            left = (abs(self.pan_distance) // 2) + offset_x
            top = (abs(self.pan_distance) // 2) + offset_y
            cropped = expanded.crop((left, top, left + w, top + h))
            
            return np.array(cropped)
        
        return VideoClip(make_frame, duration=duration).with_fps(clip.fps)
    
    def apply_all_transitions(self, clip: VideoClip, apply_ken_burns: bool = True, 
                            apply_pan: bool = True) -> VideoClip:
        """Applique toutes les transitions à un clip
        
        Args:
            clip: Le clip vidéo
            apply_ken_burns: Appliquer l'effet Ken Burns
            apply_pan: Appliquer l'effet pan
        """
        logger.info(f"Application des transitions: ken_burns={apply_ken_burns}, pan={apply_pan}")
        
        # Appliquer fade-in et fade-out de base
        clip = self.apply_fade_in(clip)
        clip = self.apply_fade_out(clip)
        
        # Appliquer Ken Burns si activé
        if apply_ken_burns and clip.duration > 1.0:
            # Alterner entre zoom avant et zoom arrière pour varier
            zoom_in = random.choice([True, False])
            clip = self.apply_ken_burns(clip, zoom_in=zoom_in)
            logger.info(f"Effet Ken Burns appliqué (zoom_in={zoom_in})")
        
        # Appliquer pan si activé
        if apply_pan and clip.duration > 1.0:
            clip = self.apply_pan(clip, direction='random')
            logger.info("Effet pan appliqué")
        
        return clip


def create_crossfade_transition(clip1: VideoClip, clip2: VideoClip, 
                               duration: float = 0.5) -> VideoClip:
    """Crée une transition crossfade entre deux clips
    
    Args:
        clip1: Premier clip (sortant)
        clip2: Deuxième clip (entrant)
        duration: Durée de la transition en secondes
    
    Returns:
        Clip composite avec transition
    """
    # Pour MoviePy 2.x, crossfade temporairement désactivé
    # TODO: Implémenter avec la nouvelle API
    logger.info("Transition crossfade temporairement désactivée pour MoviePy 2.x")
    
    # Retourner simplement la concaténation des clips
    from moviepy import concatenate_videoclips
    return concatenate_videoclips([clip1, clip2], method="compose")
