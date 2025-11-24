"""Models pour les timestamps et items de vidéo"""
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid


class TimestampItem(BaseModel):
    """Représente un élément de timestamp avec image et durée"""
    text: str
    image_path: Optional[str] = None
    start_time_ms: int
    end_time_ms: int
    confidence: Optional[float] = None

    def get_duration_seconds(self) -> float:
        """Calcule la durée en secondes"""
        return (self.end_time_ms - self.start_time_ms) / 1000.0


class Timestamp(BaseModel):
    """Représente une collection de timestamps pour une vidéo"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    idea_id: str
    timestamps: List[TimestampItem] = []
    total_duration_ms: int = 0

    def get_total_duration_seconds(self) -> float:
        """Calcule la durée totale en secondes"""
        return self.total_duration_ms / 1000.0
