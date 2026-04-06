"""
Vector store and retrieval system for disaster data
"""
import asyncio
import math
from typing import Dict, List

from rag.config.settings import TOP_K_RESULTS
from rag.database.db_init import load_rescue_operations, load_shelters


class VectorStore:
    """Vector store for efficient retrieval of relevant documents"""
    
    def __init__(self):
        """Initialize vector store with embeddings"""
        try:
            from rag.utils.embeddings import EmbeddingModel

            self.embeddings = EmbeddingModel()
        except Exception as exc:
            print(f"⚠ Embedding model unavailable ({exc}), using fallback")
            from rag.utils.embeddings import SimpleEmbedding
            self.embeddings = SimpleEmbedding()
        
        self.shelters = []
        self.operations = []
        self.shelter_embeddings = []
        self.operation_embeddings = []
        
        self._load_data()
    
    def _load_data(self):
        """Load and embed all documents"""
        # Load shelters
        shelters_data = load_shelters()
        self.shelters = shelters_data
        
        # Create searchable text for shelters
        shelter_texts = [
            f"{s['name']} {s['location']} {' '.join(s['amenities'])}"
            for s in shelters_data
        ]
        self.shelter_embeddings = self.embeddings.embed_texts(shelter_texts)
        
        # Load operations
        operations_data = load_rescue_operations()
        self.operations = operations_data
        
        # Create searchable text for operations
        operation_texts = [
            f"{o['location']} {o['severity']} {' '.join(o['techniques_used'])} {o['lessons_learned']}"
            for o in operations_data
        ]
        self.operation_embeddings = self.embeddings.embed_texts(operation_texts)
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates (Haversine formula)
        
        Args:
            lat1, lon1: First coordinate
            lat2, lon2: Second coordinate
            
        Returns:
            Distance in kilometers
        """
        R = 6371  # Earth radius in km
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def retrieve_shelters(self, latitude: float, longitude: float, 
                         query_text: str, top_k: int = TOP_K_RESULTS) -> List[Dict]:
        """
        Retrieve relevant shelters based on location and query
        
        Args:
            latitude: Flood location latitude
            longitude: Flood location longitude
            query_text: Query text for semantic search
            top_k: Number of results
            
        Returns:
            List of relevant shelters with distances
        """
        # Semantic search
        query_embedding = self.embeddings.embed_text(query_text)
        
        from sklearn.metrics.pairwise import cosine_similarity
        similarities = cosine_similarity([query_embedding], self.shelter_embeddings)[0]
        
        # Combine semantic relevance with proximity
        scored_shelters = []
        for i, shelter in enumerate(self.shelters):
            distance = self._calculate_distance(
                latitude, longitude,
                shelter['latitude'], shelter['longitude']
            )
            
            # Score: 70% semantic, 30% proximity (closer = better)
            proximity_score = max(0, 1 - (distance / 50))  # Normalize to 50km radius
            combined_score = (similarities[i] * 0.7) + (proximity_score * 0.3)
            
            scored_shelters.append({
                **shelter,
                'distance_km': round(distance, 2),
                'relevance_score': round(combined_score, 3)
            })
        
        # Sort by combined score
        scored_shelters.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return scored_shelters[:top_k]

    async def retrieve_shelters_async(
        self, latitude: float, longitude: float, query_text: str, top_k: int = TOP_K_RESULTS
    ) -> List[Dict]:
        return await asyncio.to_thread(self.retrieve_shelters, latitude, longitude, query_text, top_k)
    
    def retrieve_operations(self, latitude: float, longitude: float,
                           severity: str, query_text: str,
                           top_k: int = TOP_K_RESULTS) -> List[Dict]:
        """
        Retrieve relevant historical operations
        
        Args:
            latitude: Flood location latitude
            longitude: Flood location longitude
            severity: Severity level
            query_text: Query text
            top_k: Number of results
            
        Returns:
            List of relevant operations
        """
        # Semantic search
        query_embedding = self.embeddings.embed_text(query_text)
        
        from sklearn.metrics.pairwise import cosine_similarity
        similarities = cosine_similarity([query_embedding], self.operation_embeddings)[0]
        
        # Combine semantic relevance with proximity
        scored_operations = []
        for i, operation in enumerate(self.operations):
            distance = self._calculate_distance(
                latitude, longitude,
                operation['latitude'], operation['longitude']
            )
            
            # Score based on semantic match and proximity
            proximity_score = max(0, 1 - (distance / 100))  # Wider radius for history
            
            # Severity match bonus
            severity_match = 1.0 if operation['severity'] == severity else 0.5
            
            combined_score = (similarities[i] * 0.5) + (proximity_score * 0.3) + (severity_match * 0.2)
            
            scored_operations.append({
                **operation,
                'distance_km': round(distance, 2),
                'relevance_score': round(combined_score, 3)
            })
        
        # Sort by score
        scored_operations.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return scored_operations[:top_k]

    async def retrieve_operations_async(
        self, latitude: float, longitude: float, severity: str, query_text: str, top_k: int = TOP_K_RESULTS
    ) -> List[Dict]:
        return await asyncio.to_thread(self.retrieve_operations, latitude, longitude, severity, query_text, top_k)
    
    def get_best_techniques(self, operations: List[Dict], severity: str = None) -> List[str]:
        """
        Extract best techniques from retrieved operations and filter by severity
        
        Args:
            operations: List of relevant operations
            severity: Flood severity level (low, medium, high, critical)
            
        Returns:
            List of recommended techniques (curated and realistic)
        """
        # Realistic techniques for each severity level
        TECHNIQUES_BY_SEVERITY = {
            'low': [
                'Wading Rescue',
                'Manual Wading',
                'Door-to-Door Rescue',
                'Community Coordination'
            ],
            'medium': [
                'Rubber Boat Rescue',
                'High-Speed Rescue Boats',
                'Amphibious Vehicles',
                'Rope Lines',
                'Swimming Team Rescue',
                'Manual Wading'
            ],
            'high': [
                'High-Speed Rescue Boats',
                'Rubber Boat Rescue',
                'Amphibious Vehicles',
                'Helicopter Evacuation',
                'Rope Rescue',
                'Swimming Rescue Teams',
                'Building Rappelling'
            ],
            'critical': [
                'Helicopter Evacuation',
                'High-Speed Rescue Boats',
                'Amphibious Vehicles',
                'Rope Rescue',
                'Swimming Rescue Teams',
                'Helicopter Rescue',
                'Building Rappelling',
                'Boat Shuttle Service'
            ]
        }
        
        # Get frequency-based techniques from operations
        techniques_count = {}
        for op in operations:
            for technique in op['techniques_used']:
                techniques_count[technique] = techniques_count.get(technique, 0) + 1
        
        # Filter by severity if provided
        if severity and severity in TECHNIQUES_BY_SEVERITY:
            allowed_techniques = set(TECHNIQUES_BY_SEVERITY[severity])
            techniques_count = {t: c for t, c in techniques_count.items() if t in allowed_techniques}
        
        # Sort by frequency and return top 8
        sorted_techniques = sorted(techniques_count.items(), key=lambda x: x[1], reverse=True)
        return [t[0] for t in sorted_techniques[:8]]

    async def get_best_techniques_async(self, operations: List[Dict], severity: str = None) -> List[str]:
        return await asyncio.to_thread(self.get_best_techniques, operations, severity)
    
    def get_required_resources(self, operations: List[Dict]) -> List[str]:
        """
        Extract required resources from operations
        
        Args:
            operations: List of relevant operations
            
        Returns:
            List of recommended resources
        """
        resources_count = {}
        for op in operations:
            for resource in op['resources_deployed']:
                resources_count[resource] = resources_count.get(resource, 0) + 1
        
        # Sort by frequency
        sorted_resources = sorted(resources_count.items(), key=lambda x: x[1], reverse=True)
        return [r[0] for r in sorted_resources]

    async def get_required_resources_async(self, operations: List[Dict]) -> List[str]:
        return await asyncio.to_thread(self.get_required_resources, operations)
