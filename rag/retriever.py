# """
# Vector store and retrieval system for disaster data
# """
# import json
# from pathlib import Path
# from typing import List, Dict, Tuple
# import math
# from utils.embeddings import EmbeddingModel
# from utils.text_processing import format_shelter_context, format_operation_context
# from database.db_init import load_shelters, load_rescue_operations
# from config.settings import TOP_K_RESULTS


# class VectorStore:
#     """Vector store for efficient retrieval of relevant documents"""
    
#     def __init__(self):
#         """Initialize vector store with embeddings"""
#         try:
#             self.embeddings = EmbeddingModel()
#         except ImportError:
#             print("⚠ Sentence transformers not available, using fallback")
#             from utils.embeddings import SimpleEmbedding
#             self.embeddings = SimpleEmbedding()
        
#         self.shelters = []
#         self.operations = []
#         self.shelter_embeddings = []
#         self.operation_embeddings = []
        
#         self._load_data()
    
#     def _load_data(self):
#         """Load and embed all documents"""
#         # Load shelters
#         shelters_data = load_shelters()
#         self.shelters = shelters_data
        
#         # Create searchable text for shelters
#         shelter_texts = [
#             f"{s['name']} {s['location']} {' '.join(s['amenities'])}"
#             for s in shelters_data
#         ]
#         self.shelter_embeddings = self.embeddings.embed_texts(shelter_texts)
        
#         # Load operations
#         operations_data = load_rescue_operations()
#         self.operations = operations_data
        
#         # Create searchable text for operations
#         operation_texts = [
#             f"{o['location']} {o['severity']} {' '.join(o['techniques_used'])} {o['lessons_learned']}"
#             for o in operations_data
#         ]
#         self.operation_embeddings = self.embeddings.embed_texts(operation_texts)
    
#     def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
#         """
#         Calculate distance between two coordinates (Haversine formula)
        
#         Args:
#             lat1, lon1: First coordinate
#             lat2, lon2: Second coordinate
            
#         Returns:
#             Distance in kilometers
#         """
#         R = 6371  # Earth radius in km
        
#         phi1 = math.radians(lat1)
#         phi2 = math.radians(lat2)
#         delta_phi = math.radians(lat2 - lat1)
#         delta_lambda = math.radians(lon2 - lon1)
        
#         a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
#         c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
#         return R * c
    
#     def retrieve_shelters(self, latitude: float, longitude: float, 
#                          query_text: str, top_k: int = TOP_K_RESULTS) -> List[Dict]:
#         """
#         Retrieve relevant shelters based on location and query
        
#         Args:
#             latitude: Flood location latitude
#             longitude: Flood location longitude
#             query_text: Query text for semantic search
#             top_k: Number of results
            
#         Returns:
#             List of relevant shelters with distances
#         """
#         # Semantic search
#         query_embedding = self.embeddings.embed_text(query_text)
        
#         from sklearn.metrics.pairwise import cosine_similarity
#         similarities = cosine_similarity([query_embedding], self.shelter_embeddings)[0]
        
#         # Combine semantic relevance with proximity
#         scored_shelters = []
#         for i, shelter in enumerate(self.shelters):
#             distance = self._calculate_distance(
#                 latitude, longitude,
#                 shelter['latitude'], shelter['longitude']
#             )
            
#             # Score: 70% semantic, 30% proximity (closer = better)
#             proximity_score = max(0, 1 - (distance / 50))  # Normalize to 50km radius
#             combined_score = (similarities[i] * 0.7) + (proximity_score * 0.3)
            
#             scored_shelters.append({
#                 **shelter,
#                 'distance_km': round(distance, 2),
#                 'relevance_score': round(combined_score, 3)
#             })
        
#         # Sort by combined score
#         scored_shelters.sort(key=lambda x: x['relevance_score'], reverse=True)
        
#         return scored_shelters[:top_k]
    
#     def retrieve_operations(self, latitude: float, longitude: float,
#                            severity: str, query_text: str,
#                            top_k: int = TOP_K_RESULTS) -> List[Dict]:
#         """
#         Retrieve relevant historical operations
        
#         Args:
#             latitude: Flood location latitude
#             longitude: Flood location longitude
#             severity: Severity level
#             query_text: Query text
#             top_k: Number of results
            
#         Returns:
#             List of relevant operations
#         """
#         # Semantic search
#         query_embedding = self.embeddings.embed_text(query_text)
        
#         from sklearn.metrics.pairwise import cosine_similarity
#         similarities = cosine_similarity([query_embedding], self.operation_embeddings)[0]
        
#         # Combine semantic relevance with proximity
#         scored_operations = []
#         for i, operation in enumerate(self.operations):
#             distance = self._calculate_distance(
#                 latitude, longitude,
#                 operation['latitude'], operation['longitude']
#             )
            
#             # Score based on semantic match and proximity
#             proximity_score = max(0, 1 - (distance / 100))  # Wider radius for history
            
#             # Severity match bonus
#             severity_match = 1.0 if operation['severity'] == severity else 0.5
            
#             combined_score = (similarities[i] * 0.5) + (proximity_score * 0.3) + (severity_match * 0.2)
            
#             scored_operations.append({
#                 **operation,
#                 'distance_km': round(distance, 2),
#                 'relevance_score': round(combined_score, 3)
#             })
        
#         # Sort by score
#         scored_operations.sort(key=lambda x: x['relevance_score'], reverse=True)
        
#         return scored_operations[:top_k]
    
#     def get_best_techniques(self, operations: List[Dict], severity: str = None) -> List[str]:
#         """
#         Extract best techniques from retrieved operations and filter by severity
        
#         Args:
#             operations: List of relevant operations
#             severity: Flood severity level (low, medium, high, critical)
            
#         Returns:
#             List of recommended techniques (curated and realistic)
#         """
#         # Realistic techniques for each severity level
#         TECHNIQUES_BY_SEVERITY = {
#             'low': [
#                 'Wading Rescue',
#                 'Manual Wading',
#                 'Door-to-Door Rescue',
#                 'Community Coordination'
#             ],
#             'medium': [
#                 'Rubber Boat Rescue',
#                 'High-Speed Rescue Boats',
#                 'Amphibious Vehicles',
#                 'Rope Lines',
#                 'Swimming Team Rescue',
#                 'Manual Wading'
#             ],
#             'high': [
#                 'High-Speed Rescue Boats',
#                 'Rubber Boat Rescue',
#                 'Amphibious Vehicles',
#                 'Helicopter Evacuation',
#                 'Rope Rescue',
#                 'Swimming Rescue Teams',
#                 'Building Rappelling'
#             ],
#             'critical': [
#                 'Helicopter Evacuation',
#                 'High-Speed Rescue Boats',
#                 'Amphibious Vehicles',
#                 'Rope Rescue',
#                 'Swimming Rescue Teams',
#                 'Helicopter Rescue',
#                 'Building Rappelling',
#                 'Boat Shuttle Service'
#             ]
#         }
        
#         # Get frequency-based techniques from operations
#         techniques_count = {}
#         for op in operations:
#             for technique in op['techniques_used']:
#                 techniques_count[technique] = techniques_count.get(technique, 0) + 1
        
#         # Filter by severity if provided
#         if severity and severity in TECHNIQUES_BY_SEVERITY:
#             allowed_techniques = set(TECHNIQUES_BY_SEVERITY[severity])
#             techniques_count = {t: c for t, c in techniques_count.items() if t in allowed_techniques}
        
#         # Sort by frequency and return top 8
#         sorted_techniques = sorted(techniques_count.items(), key=lambda x: x[1], reverse=True)
#         return [t[0] for t in sorted_techniques[:8]]
    
#     def get_required_resources(self, operations: List[Dict]) -> List[str]:
#         """
#         Extract required resources from operations
        
#         Args:
#             operations: List of relevant operations
            
#         Returns:
#             List of recommended resources
#         """
#         resources_count = {}
#         for op in operations:
#             for resource in op['resources_deployed']:
#                 resources_count[resource] = resources_count.get(resource, 0) + 1
        
#         # Sort by frequency
#         sorted_resources = sorted(resources_count.items(), key=lambda x: x[1], reverse=True)
#         return [r[0] for r in sorted_resources]


"""
Vector store and retrieval system for disaster data — LangChain version
Input  : latitude (float), longitude (float), query_text (str), severity (str)
Output : List[Dict] for shelters/operations; List[str] for techniques/resources
"""

import math
from typing import List, Dict, Optional

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document

from database.db_init import load_shelters, load_rescue_operations
from config.settings import TOP_K_RESULTS


# ---------------------------------------------------------------------------
# Severity → allowed rescue techniques (same curated set as original)
# ---------------------------------------------------------------------------
TECHNIQUES_BY_SEVERITY: Dict[str, List[str]] = {
    "low": [
        "Wading Rescue",
        "Manual Wading",
        "Door-to-Door Rescue",
        "Community Coordination",
    ],
    "medium": [
        "Rubber Boat Rescue",
        "High-Speed Rescue Boats",
        "Amphibious Vehicles",
        "Rope Lines",
        "Swimming Team Rescue",
        "Manual Wading",
    ],
    "high": [
        "High-Speed Rescue Boats",
        "Rubber Boat Rescue",
        "Amphibious Vehicles",
        "Helicopter Evacuation",
        "Rope Rescue",
        "Swimming Rescue Teams",
        "Building Rappelling",
    ],
    "critical": [
        "Helicopter Evacuation",
        "High-Speed Rescue Boats",
        "Amphibious Vehicles",
        "Rope Rescue",
        "Swimming Rescue Teams",
        "Helicopter Rescue",
        "Building Rappelling",
        "Boat Shuttle Service",
    ],
}


# ---------------------------------------------------------------------------
# Haversine helper (identical logic to original)
# ---------------------------------------------------------------------------
def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return distance in km between two lat/lon pairs."""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ---------------------------------------------------------------------------
# VectorStore (LangChain)
# ---------------------------------------------------------------------------
class VectorStore:
    """
    LangChain-backed FAISS vector store for shelters and rescue operations.

    Inputs  (constructor) : none — loads from DB automatically
    Outputs (methods)     : see individual method docstrings
    """

    def __init__(self) -> None:
        self._embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        self.shelters: List[Dict] = []
        self.operations: List[Dict] = []
        self._shelter_store: Optional[FAISS] = None
        self._operation_store: Optional[FAISS] = None

        self._load_data()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    def _load_data(self) -> None:
        """Load raw DB records and build two FAISS indices."""
        # ── Shelters ──────────────────────────────────────────────────
        self.shelters = load_shelters()
        shelter_docs = [
            Document(
                page_content=(
                    f"{s['name']} {s['location']} {' '.join(s['amenities'])}"
                ),
                metadata={"idx": i},
            )
            for i, s in enumerate(self.shelters)
        ]
        self._shelter_store = FAISS.from_documents(shelter_docs, self._embeddings)

        # ── Operations ───────────────────────────────────────────────
        self.operations = load_rescue_operations()
        operation_docs = [
            Document(
                page_content=(
                    f"{o['location']} {o['severity']} "
                    f"{' '.join(o['techniques_used'])} {o['lessons_learned']}"
                ),
                metadata={"idx": i},
            )
            for i, o in enumerate(self.operations)
        ]
        self._operation_store = FAISS.from_documents(operation_docs, self._embeddings)

    def _score_with_proximity(
        self,
        records: List[Dict],
        lc_results: List[tuple],  # (Document, score) from similarity_search_with_score
        query_lat: float,
        query_lon: float,
        proximity_radius_km: float,
        semantic_weight: float,
        proximity_weight: float,
        severity: Optional[str] = None,
        severity_weight: float = 0.0,
    ) -> List[Dict]:
        """
        Merge FAISS semantic scores with haversine proximity scores.

        Returns list of record dicts enriched with 'distance_km' and
        'relevance_score', sorted descending by relevance_score.
        """
        # Build idx → FAISS score map (FAISS returns L2; lower = more similar)
        score_map: Dict[int, float] = {}
        max_score = max((s for _, s in lc_results), default=1.0) or 1.0
        for doc, raw_score in lc_results:
            idx = doc.metadata["idx"]
            # Normalise: invert so higher = more similar
            score_map[idx] = 1.0 - (raw_score / max_score)

        enriched: List[Dict] = []
        for i, rec in enumerate(records):
            distance = _haversine(query_lat, query_lon, rec["latitude"], rec["longitude"])
            proximity_score = max(0.0, 1.0 - (distance / proximity_radius_km))
            semantic_score = score_map.get(i, 0.0)

            combined = (semantic_score * semantic_weight) + (proximity_score * proximity_weight)

            if severity and severity_weight:
                sev_match = 1.0 if rec.get("severity") == severity else 0.5
                combined += sev_match * severity_weight

            enriched.append(
                {**rec, "distance_km": round(distance, 2), "relevance_score": round(combined, 3)}
            )

        enriched.sort(key=lambda x: x["relevance_score"], reverse=True)
        return enriched

    # ------------------------------------------------------------------
    # Public API  (same signatures as original VectorStore)
    # ------------------------------------------------------------------
    def retrieve_shelters(
        self,
        latitude: float,
        longitude: float,
        query_text: str,
        top_k: int = TOP_K_RESULTS,
    ) -> List[Dict]:
        """
        Retrieve relevant shelters.

        Input
        -----
        latitude    : float   – flood location latitude
        longitude   : float   – flood location longitude
        query_text  : str     – e.g. "high flood 3.5 sq km"
        top_k       : int     – number of results (default from settings)

        Output
        ------
        List[Dict] each containing all original shelter fields plus:
            distance_km     : float
            relevance_score : float  (0–1, semantic 70% + proximity 30%)
        """
        lc_results = self._shelter_store.similarity_search_with_score(
            query_text, k=len(self.shelters)
        )
        scored = self._score_with_proximity(
            self.shelters,
            lc_results,
            latitude,
            longitude,
            proximity_radius_km=50.0,
            semantic_weight=0.7,
            proximity_weight=0.3,
        )
        return scored[:top_k]

    def retrieve_operations(
        self,
        latitude: float,
        longitude: float,
        severity: str,
        query_text: str,
        top_k: int = TOP_K_RESULTS,
    ) -> List[Dict]:
        """
        Retrieve relevant historical rescue operations.

        Input
        -----
        latitude    : float  – flood location latitude
        longitude   : float  – flood location longitude
        severity    : str    – one of: low | medium | high | critical
        query_text  : str    – e.g. "high flood rescue techniques"
        top_k       : int    – number of results

        Output
        ------
        List[Dict] each containing all original operation fields plus:
            distance_km     : float
            relevance_score : float  (semantic 50% + proximity 30% + severity 20%)
        """
        lc_results = self._operation_store.similarity_search_with_score(
            query_text, k=len(self.operations)
        )
        scored = self._score_with_proximity(
            self.operations,
            lc_results,
            latitude,
            longitude,
            proximity_radius_km=100.0,
            semantic_weight=0.5,
            proximity_weight=0.3,
            severity=severity,
            severity_weight=0.2,
        )
        return scored[:top_k]

    def get_best_techniques(
        self,
        operations: List[Dict],
        severity: Optional[str] = None,
    ) -> List[str]:
        """
        Extract frequency-ranked rescue techniques, filtered by severity.

        Input
        -----
        operations : List[Dict]  – output of retrieve_operations()
        severity   : str | None  – filter key (low/medium/high/critical)

        Output
        ------
        List[str]  – up to 8 technique names, sorted by historical frequency
        """
        counts: Dict[str, int] = {}
        for op in operations:
            for tech in op["techniques_used"]:
                counts[tech] = counts.get(tech, 0) + 1

        if severity and severity in TECHNIQUES_BY_SEVERITY:
            allowed = set(TECHNIQUES_BY_SEVERITY[severity])
            counts = {t: c for t, c in counts.items() if t in allowed}

        sorted_techs = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return [t for t, _ in sorted_techs[:8]]

    def get_required_resources(self, operations: List[Dict]) -> List[str]:
        """
        Extract frequency-ranked resources from historical operations.

        Input
        -----
        operations : List[Dict]  – output of retrieve_operations()

        Output
        ------
        List[str]  – resource names sorted by historical frequency (no limit)
        """
        counts: Dict[str, int] = {}
        for op in operations:
            for res in op["resources_deployed"]:
                counts[res] = counts.get(res, 0) + 1

        sorted_res = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return [r for r, _ in sorted_res]