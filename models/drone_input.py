"""
Data models for drone input and RAG responses
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple, Union
from datetime import datetime
from enum import Enum


class SeverityLevel(str, Enum):
    """Flood severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DroneInput:
    """
    Input from drone detecting flood
    """
    latitude: float
    longitude: float
    flood_depth_cm: float
    severity: SeverityLevel
    affected_area_sq_km: float
    timestamp: datetime = None
    drone_id: str = "DRONE-001"
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "flood_depth_cm": self.flood_depth_cm,
            "severity": self.severity.value,
            "affected_area_sq_km": self.affected_area_sq_km,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else str(self.timestamp),
            "drone_id": self.drone_id
        }


@dataclass
class Shelter:
    """Shelter information"""
    shelter_id: str
    name: str
    location: str
    latitude: float
    longitude: float
    capacity: int
    current_occupancy: int
    amenities: List[str]
    distance_km: float = None
    
    def to_dict(self) -> Dict:
        return {
            "shelter_id": self.shelter_id,
            "name": self.name,
            "location": self.location,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "capacity": self.capacity,
            "current_occupancy": self.current_occupancy,
            "available_beds": self.capacity - self.current_occupancy,
            "amenities": self.amenities,
            "distance_km": self.distance_km
        }


@dataclass
class RescueOperation:
    """Historical rescue operation data"""
    operation_id: str
    date: str
    location: str
    latitude: float
    longitude: float
    severity: SeverityLevel
    affected_population: int
    techniques_used: List[str]
    resources_deployed: List[str]
    shelters_activated: List[str]
    duration_hours: float
    outcome: str
    lessons_learned: str
    
    def to_dict(self) -> Dict:
        return {
            "operation_id": self.operation_id,
            "date": self.date,
            "location": self.location,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "severity": self.severity.value,
            "affected_population": self.affected_population,
            "techniques_used": self.techniques_used,
            "resources_deployed": self.resources_deployed,
            "shelters_activated": self.shelters_activated,
            "duration_hours": self.duration_hours,
            "outcome": self.outcome,
            "lessons_learned": self.lessons_learned
        }


@dataclass
class RAGResponse:
    """Response from RAG system"""
    message_victim: str
    message_rescuer: str
    relevant_shelters: List[Shelter]
    relevant_operations: List[RescueOperation]
    recommended_techniques: List[str]
    resources_needed: List[str]
    confidence_score: Union[Tuple[str, str], float]  # (level, reason) or legacy float
    query_context: Dict
    
    def to_dict(self) -> Dict:
        # Handle both new tuple format and legacy float format
        if isinstance(self.confidence_score, tuple):
            confidence_level, confidence_reason = self.confidence_score
            confidence_data = {"level": confidence_level, "reason": confidence_reason}
        else:
            confidence_data = self.confidence_score
            
        return {
            "message_victim": self.message_victim,
            "message_rescuer": self.message_rescuer,
            "shelters": [s.to_dict() for s in self.relevant_shelters],
            "operations": [op.to_dict() for op in self.relevant_operations],
            "recommended_techniques": self.recommended_techniques,
            "resources_needed": self.resources_needed,
            "confidence_score": confidence_data,
            "query_context": self.query_context
        }
