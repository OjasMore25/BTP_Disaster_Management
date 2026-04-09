# """
# Main RAG Pipeline combining retrieval and generation

# """
# from typing import Dict
# from models.drone_input import DroneInput, RAGResponse, Shelter, RescueOperation, SeverityLevel
# from rag.retriever import VectorStore
# from rag.generator import DisasterResponseGenerator
# from utils.text_processing import (
#     format_drone_input, format_shelter_context, format_operation_context, merge_contexts
# )
# from utils.logger import get_logger
# from config.settings import CONFIDENCE_THRESHOLD

# logger = get_logger()


# class DisasterRAGPipeline:
#     """Main RAG pipeline for disaster response"""
    
#     def __init__(self):
#         """Initialize RAG components"""
#         logger.info("Initializing Disaster Response RAG Pipeline...")
        
#         self.vector_store = VectorStore()
#         self.generator = DisasterResponseGenerator()
        
#         logger.info("✓ RAG Pipeline initialized successfully")
    
#     def process_drone_input(self, drone_input: DroneInput) -> RAGResponse:
#         """
#         Process drone input and generate disaster response
        
#         Args:
#             drone_input: Drone detection data
            
#         Returns:
#             RAGResponse with victim and rescuer messages
#         """
#         logger.info(f"Processing drone input: {drone_input.drone_id}")
        
#         # Step 1: Format drone input
#         drone_context = format_drone_input(drone_input.to_dict())
#         logger.debug(f"Drone context: {drone_context}")
        
#         # Step 2: Retrieve relevant shelters
#         logger.info("Retrieving relevant shelters...")
#         shelter_query = f"{drone_input.severity.value} flood {drone_input.affected_area_sq_km} sq km"
#         relevant_shelters_data = self.vector_store.retrieve_shelters(
#             drone_input.latitude,
#             drone_input.longitude,
#             shelter_query,
#             top_k=5
#         )
        
#         relevant_shelters = [
#             Shelter(
#                 shelter_id=s['shelter_id'],
#                 name=s['name'],
#                 location=s['location'],
#                 latitude=s['latitude'],
#                 longitude=s['longitude'],
#                 capacity=s['capacity'],
#                 current_occupancy=s['current_occupancy'],
#                 amenities=s['amenities'],
#                 distance_km=s['distance_km']
#             )
#             for s in relevant_shelters_data
#         ]
#         logger.info(f"Found {len(relevant_shelters)} relevant shelters")
        
#         # Step 3: Retrieve relevant historical operations
#         logger.info("Retrieving relevant historical operations...")
#         operation_query = f"{drone_input.severity.value} flood rescue techniques"
#         relevant_operations_data = self.vector_store.retrieve_operations(
#             drone_input.latitude,
#             drone_input.longitude,
#             drone_input.severity.value,
#             operation_query,
#             top_k=5
#         )
        
#         relevant_operations = [
#             RescueOperation(
#                 operation_id=op['operation_id'],
#                 date=op['date'],
#                 location=op['location'],
#                 latitude=op['latitude'],
#                 longitude=op['longitude'],
#                 severity=SeverityLevel(op['severity']),
#                 affected_population=op['affected_population'],
#                 techniques_used=op['techniques_used'],
#                 resources_deployed=op['resources_deployed'],
#                 shelters_activated=op['shelters_activated'],
#                 duration_hours=op['duration_hours'],
#                 outcome=op['outcome'],
#                 lessons_learned=op['lessons_learned']
#             )
#             for op in relevant_operations_data
#         ]
#         logger.info(f"Found {len(relevant_operations)} relevant historical operations")
        
#         # Step 4: Extract recommended techniques and resources
#         recommended_techniques = self.vector_store.get_best_techniques(
#             relevant_operations_data,
#             severity=drone_input.severity.value
#         )
#         resources_needed = self.vector_store.get_required_resources(relevant_operations_data)
#         logger.info(f"Recommended techniques: {recommended_techniques}")
#         logger.info(f"Required resources: {resources_needed}")
        
#         # Step 5: Format contexts for LLM
#         shelters_text = "\n".join([format_shelter_context(s) for s in relevant_shelters_data])
#         operations_text = "\n".join([format_operation_context(op) for op in relevant_operations_data])
#         techniques_text = ", ".join(recommended_techniques)
#         resources_text = ", ".join(resources_needed)
        
#         # Step 6: Generate messages
#         logger.info("Generating victim message...")
#         victim_message = self.generator.generate_victim_message(
#             drone_context,
#             shelters_text
#         )
        
#         logger.info("Generating rescuer plan...")
#         rescuer_message = self.generator.generate_rescuer_plan(
#             drone_context,
#             operations_text,
#             techniques_text,
#             resources_text
#         )
        
#         # Step 7: Calculate confidence
#         confidence = self.generator.calculate_confidence(
#             len(relevant_operations),
#             "high" if len(relevant_shelters) >= 3 else "medium"
#         )
#         logger.info(f"Confidence score: {confidence}")
        
#         # Step 8: Create response
#         response = RAGResponse(
#             message_victim=victim_message,
#             message_rescuer=rescuer_message,
#             relevant_shelters=relevant_shelters,
#             relevant_operations=relevant_operations,
#             recommended_techniques=recommended_techniques,
#             resources_needed=resources_needed,
#             confidence_score=confidence,
#             query_context={
#                 "drone_location": f"{drone_input.latitude}, {drone_input.longitude}",
#                 "flood_severity": drone_input.severity.value,
#                 "affected_area_sq_km": drone_input.affected_area_sq_km,
#                 "flood_depth_cm": drone_input.flood_depth_cm,
#                 "timestamp": drone_input.timestamp.isoformat()
#             }
#         )
        
#         logger.info("✓ RAG pipeline processing completed")
#         return response


"""
Main RAG Pipeline — LangChain version

Input  : DroneInput (Pydantic model)
Output : RAGResponse (Pydantic model)
"""

from models.drone_input import DroneInput, RAGResponse, Shelter, RescueOperation, SeverityLevel
from rag.retriever import VectorStore
from rag.generator import DisasterResponseGenerator
from utils.text_processing import (
    format_drone_input,
    format_shelter_context,
    format_operation_context,
)
from utils.logger import get_logger
from config.settings import CONFIDENCE_THRESHOLD

logger = get_logger()


class DisasterRAGPipeline:
    """
    End-to-end LangChain RAG pipeline for disaster response.

    Input  : DroneInput  – drone detection event
    Output : RAGResponse – victim alert + rescuer plan + metadata
    """

    def __init__(self) -> None:
        logger.info("Initialising Disaster Response RAG Pipeline (LangChain)...")
        self.vector_store = VectorStore()
        self.generator = DisasterResponseGenerator()
        logger.info("✓ RAG Pipeline ready")

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------
    def process_drone_input(self, drone_input: DroneInput) -> RAGResponse:
        """
        Process one drone detection event end-to-end.

        Input
        -----
        drone_input : DroneInput
            Required fields
            ───────────────
            drone_id            : str
            latitude            : float
            longitude           : float
            severity            : SeverityLevel  (low|medium|high|critical)
            affected_area_sq_km : float
            flood_depth_cm      : float
            timestamp           : datetime

        Output
        ------
        RAGResponse
            message_victim        : str        – ≤50-word 3-bullet victim alert
            message_rescuer       : str        – multi-section rescuer plan
            relevant_shelters     : List[Shelter]
            relevant_operations   : List[RescueOperation]
            recommended_techniques: List[str]
            resources_needed      : List[str]
            confidence_score      : Tuple[str, str]  – ("HIGH"|"MEDIUM"|"LOW", reason)
            query_context         : Dict[str, Any]
        """
        logger.info(f"Processing drone input: {drone_input.drone_id}")

        # ── Step 1 : format drone context ────────────────────────────────
        drone_context: str = format_drone_input(drone_input.to_dict())

        # ── Step 2 : retrieve shelters ───────────────────────────────────
        shelter_query = (
            f"{drone_input.severity.value} flood "
            f"{drone_input.affected_area_sq_km} sq km"
        )
        raw_shelters = self.vector_store.retrieve_shelters(
            drone_input.latitude,
            drone_input.longitude,
            shelter_query,
            top_k=5,
        )
        relevant_shelters = [
            Shelter(
                shelter_id=s["shelter_id"],
                name=s["name"],
                location=s["location"],
                latitude=s["latitude"],
                longitude=s["longitude"],
                capacity=s["capacity"],
                current_occupancy=s["current_occupancy"],
                amenities=s["amenities"],
                distance_km=s["distance_km"],
            )
            for s in raw_shelters
        ]
        logger.info(f"Shelters retrieved: {len(relevant_shelters)}")

        # ── Step 3 : retrieve historical operations ───────────────────────
        operation_query = f"{drone_input.severity.value} flood rescue techniques"
        raw_operations = self.vector_store.retrieve_operations(
            drone_input.latitude,
            drone_input.longitude,
            drone_input.severity.value,
            operation_query,
            top_k=5,
        )
        relevant_operations = [
            RescueOperation(
                operation_id=op["operation_id"],
                date=op["date"],
                location=op["location"],
                latitude=op["latitude"],
                longitude=op["longitude"],
                severity=SeverityLevel(op["severity"]),
                affected_population=op["affected_population"],
                techniques_used=op["techniques_used"],
                resources_deployed=op["resources_deployed"],
                shelters_activated=op["shelters_activated"],
                duration_hours=op["duration_hours"],
                outcome=op["outcome"],
                lessons_learned=op["lessons_learned"],
            )
            for op in raw_operations
        ]
        logger.info(f"Operations retrieved: {len(relevant_operations)}")

        # ── Step 4 : derive techniques & resources ───────────────────────
        recommended_techniques = self.vector_store.get_best_techniques(
            raw_operations, severity=drone_input.severity.value
        )
        resources_needed = self.vector_store.get_required_resources(raw_operations)

        # ── Step 5 : build LLM context strings ───────────────────────────
        shelters_text: str = "\n".join(
            format_shelter_context(s) for s in raw_shelters
        )
        operations_text: str = "\n".join(
            format_operation_context(op) for op in raw_operations
        )
        techniques_text: str = ", ".join(recommended_techniques)
        resources_text: str = ", ".join(resources_needed)

        # ── Step 6 : generate messages ────────────────────────────────────
        logger.info("Generating victim message…")
        victim_message: str = self.generator.generate_victim_message(
            drone_context, shelters_text
        )

        logger.info("Generating rescuer plan…")
        rescuer_message: str = self.generator.generate_rescuer_plan(
            drone_context, operations_text, techniques_text, resources_text
        )

        # ── Step 7 : confidence score ─────────────────────────────────────
        shelter_quality = "high" if len(relevant_shelters) >= 3 else "medium"
        confidence = self.generator.calculate_confidence(
            len(relevant_operations), shelter_quality
        )
        logger.info(f"Confidence: {confidence}")

        # ── Step 8 : assemble response ────────────────────────────────────
        return RAGResponse(
            message_victim=victim_message,
            message_rescuer=rescuer_message,
            relevant_shelters=relevant_shelters,
            relevant_operations=relevant_operations,
            recommended_techniques=recommended_techniques,
            resources_needed=resources_needed,
            confidence_score=confidence,
            query_context={
                "drone_location": f"{drone_input.latitude}, {drone_input.longitude}",
                "flood_severity": drone_input.severity.value,
                "affected_area_sq_km": drone_input.affected_area_sq_km,
                "flood_depth_cm": drone_input.flood_depth_cm,
                "timestamp": drone_input.timestamp.isoformat(),
            },
        )