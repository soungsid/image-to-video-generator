"""Effets visuels animés pour les vidéos (pluie, neige, feu)"""
import numpy as np
from moviepy.editor import VideoClip
import random
import logging

logger = logging.getLogger(__name__)


class Particle:
    """Représente une particule animée"""
    def __init__(self, x: float, y: float, speed: float, size: int, opacity: float = 1.0):
        self.x = x
        self.y = y
        self.speed = speed
        self.size = size
        self.opacity = opacity


class WeatherEffect:
    """Classe de base pour les effets météo"""
    
    def __init__(self, width: int, height: int, intensity: float = 0.3):
        """
        Args:
            width: Largeur de la vidéo
            height: Hauteur de la vidéo
            intensity: Intensité de l'effet (0.0 à 1.0)
        """
        self.width = width
        self.height = height
        self.intensity = max(0.0, min(1.0, intensity))
        self.particles = []
    
    def create_overlay(self, duration: float, fps: int = 24) -> VideoClip:
        """Crée un overlay animé"""
        raise NotImplementedError


class RainEffect(WeatherEffect):
    """Effet de pluie"""
    
    def __init__(self, width: int, height: int, intensity: float = 0.3):
        super().__init__(width, height, intensity)
        # Nombre de gouttes basé sur l'intensité
        self.num_drops = int(100 * self.intensity)
        self._initialize_particles()
    
    def _initialize_particles(self):
        """Initialise les particules de pluie"""
        self.particles = []
        for _ in range(self.num_drops):
            x = random.uniform(0, self.width)
            y = random.uniform(-self.height, 0)
            speed = random.uniform(800, 1200) * self.intensity
            size = random.randint(1, 3)
            opacity = random.uniform(0.3, 0.7)
            self.particles.append(Particle(x, y, speed, size, opacity))
    
    def create_overlay(self, duration: float, fps: int = 24) -> VideoClip:
        """Crée l'overlay de pluie"""
        def make_frame(t):
            # Créer un frame transparent
            frame = np.zeros((self.height, self.width, 4), dtype=np.uint8)
            
            for particle in self.particles:
                # Mettre à jour la position
                particle.y += particle.speed / fps
                
                # Réinitialiser si hors écran
                if particle.y > self.height:
                    particle.y = random.uniform(-100, 0)
                    particle.x = random.uniform(0, self.width)
                
                # Dessiner la goutte (ligne verticale)
                x = int(particle.x)
                y = int(particle.y)
                
                if 0 <= x < self.width and 0 <= y < self.height:
                    # Ligne de pluie
                    for i in range(particle.size * 3):
                        y_pos = y + i
                        if 0 <= y_pos < self.height:
                            alpha = int(255 * particle.opacity * 0.7)
                            frame[y_pos, x] = [200, 200, 255, alpha]  # Bleu-gris
            
            return frame
        
        return VideoClip(make_frame, duration=duration, ismask=False).set_fps(fps)


class SnowEffect(WeatherEffect):
    """Effet de neige"""
    
    def __init__(self, width: int, height: int, intensity: float = 0.3):
        super().__init__(width, height, intensity)
        self.num_flakes = int(80 * self.intensity)
        self._initialize_particles()
    
    def _initialize_particles(self):
        """Initialise les flocons de neige"""
        self.particles = []
        for _ in range(self.num_flakes):
            x = random.uniform(0, self.width)
            y = random.uniform(-self.height, 0)
            speed = random.uniform(50, 150) * self.intensity  # Plus lent que la pluie
            size = random.randint(2, 6)
            opacity = random.uniform(0.5, 0.9)
            particle = Particle(x, y, speed, size, opacity)
            # Ajouter un mouvement horizontal aléatoire
            particle.drift = random.uniform(-20, 20)
            self.particles.append(particle)
    
    def create_overlay(self, duration: float, fps: int = 24) -> VideoClip:
        """Crée l'overlay de neige"""
        def make_frame(t):
            frame = np.zeros((self.height, self.width, 4), dtype=np.uint8)
            
            for particle in self.particles:
                # Mettre à jour la position
                particle.y += particle.speed / fps
                particle.x += particle.drift / fps  # Mouvement latéral
                
                # Réinitialiser si hors écran
                if particle.y > self.height:
                    particle.y = random.uniform(-100, 0)
                    particle.x = random.uniform(0, self.width)
                
                # Garder dans les limites horizontales
                if particle.x < 0:
                    particle.x = self.width
                elif particle.x > self.width:
                    particle.x = 0
                
                # Dessiner le flocon (cercle blanc)
                x = int(particle.x)
                y = int(particle.y)
                
                if 0 <= x < self.width and 0 <= y < self.height:
                    # Dessiner un cercle simple
                    for dx in range(-particle.size, particle.size + 1):
                        for dy in range(-particle.size, particle.size + 1):
                            if dx*dx + dy*dy <= particle.size*particle.size:
                                px = x + dx
                                py = y + dy
                                if 0 <= px < self.width and 0 <= py < self.height:
                                    alpha = int(255 * particle.opacity)
                                    frame[py, px] = [255, 255, 255, alpha]
            
            return frame
        
        return VideoClip(make_frame, duration=duration, ismask=False).set_fps(fps)


class FireEffect(WeatherEffect):
    """Effet de feu/flammes"""
    
    def __init__(self, width: int, height: int, intensity: float = 0.3):
        super().__init__(width, height, intensity)
        self.num_particles = int(150 * self.intensity)
        self._initialize_particles()
    
    def _initialize_particles(self):
        """Initialise les particules de feu"""
        self.particles = []
        # Les flammes partent du bas de l'écran
        for _ in range(self.num_particles):
            x = random.uniform(self.width * 0.3, self.width * 0.7)  # Centré
            y = random.uniform(self.height * 0.8, self.height)  # Bas de l'écran
            speed = random.uniform(200, 400) * self.intensity
            size = random.randint(3, 8)
            opacity = random.uniform(0.3, 0.8)
            particle = Particle(x, y, speed, size, opacity)
            # Mouvement horizontal aléatoire pour effet de vacillement
            particle.drift = random.uniform(-30, 30)
            # Couleur aléatoire (orange/rouge/jaune)
            particle.color = random.choice([
                [255, 100, 0],   # Orange
                [255, 50, 0],    # Rouge-orange
                [255, 200, 0],   # Jaune-orange
                [200, 0, 0],     # Rouge
            ])
            self.particles.append(particle)
    
    def create_overlay(self, duration: float, fps: int = 24) -> VideoClip:
        """Crée l'overlay de feu"""
        def make_frame(t):
            frame = np.zeros((self.height, self.width, 4), dtype=np.uint8)
            
            for particle in self.particles:
                # Mettre à jour la position (monte vers le haut)
                particle.y -= particle.speed / fps
                particle.x += particle.drift / fps
                
                # Diminuer l'opacité en montant
                particle.opacity *= 0.98
                
                # Réinitialiser si hors écran ou trop transparent
                if particle.y < 0 or particle.opacity < 0.1:
                    particle.x = random.uniform(self.width * 0.3, self.width * 0.7)
                    particle.y = random.uniform(self.height * 0.8, self.height)
                    particle.opacity = random.uniform(0.5, 0.9)
                    particle.drift = random.uniform(-30, 30)
                
                # Dessiner la particule
                x = int(particle.x)
                y = int(particle.y)
                
                if 0 <= x < self.width and 0 <= y < self.height:
                    # Dessiner un cercle avec dégradé
                    for dx in range(-particle.size, particle.size + 1):
                        for dy in range(-particle.size, particle.size + 1):
                            dist = np.sqrt(dx*dx + dy*dy)
                            if dist <= particle.size:
                                px = x + dx
                                py = y + dy
                                if 0 <= px < self.width and 0 <= py < self.height:
                                    # Dégradé depuis le centre
                                    fade = 1.0 - (dist / particle.size)
                                    alpha = int(255 * particle.opacity * fade)
                                    r, g, b = particle.color
                                    frame[py, px] = [r, g, b, alpha]
            
            return frame
        
        return VideoClip(make_frame, duration=duration, ismask=False).set_fps(fps)


class EffectManager:
    """Gestionnaire des effets visuels"""
    
    AVAILABLE_EFFECTS = {
        'rain': RainEffect,
        'snow': SnowEffect,
        'fire': FireEffect,
    }
    
    @staticmethod
    def create_effect(effect_type: str, width: int, height: int, 
                     intensity: float = 0.3) -> WeatherEffect:
        """Crée un effet
        
        Args:
            effect_type: Type d'effet ('rain', 'snow', 'fire')
            width: Largeur de la vidéo
            height: Hauteur de la vidéo
            intensity: Intensité de l'effet (0.0 à 1.0)
        
        Returns:
            Instance de l'effet
        """
        effect_class = EffectManager.AVAILABLE_EFFECTS.get(effect_type.lower())
        if not effect_class:
            raise ValueError(f"Effet inconnu: {effect_type}. Disponibles: {list(EffectManager.AVAILABLE_EFFECTS.keys())}")
        
        logger.info(f"Création de l'effet {effect_type} avec intensité {intensity}")
        return effect_class(width, height, intensity)
