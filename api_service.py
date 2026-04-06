"""
FastAPI service for Disaster Response RAG System
Provides REST endpoints for drone input and response generation
"""
import asyncio

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    from typing import List
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

from rag.models.drone_input import DroneInput, SeverityLevel
from rag.rag.rag_pipeline import DisasterRAGPipeline
from rag.utils.logger import get_logger

if not HAS_FASTAPI:
    raise ImportError("FastAPI not installed. Install with: pip install fastapi uvicorn")

logger = get_logger()
app = FastAPI(
    title="Disaster Response RAG API",
    description="RAG system for flood disaster response",
    version="1.0.0"
)

_pipeline: DisasterRAGPipeline | None = None
_pipeline_init_error: str | None = None
_pipeline_lock = asyncio.Lock()


async def _get_pipeline() -> DisasterRAGPipeline:
    global _pipeline
    global _pipeline_init_error

    if _pipeline is not None:
        return _pipeline

    async with _pipeline_lock:
        if _pipeline is not None:
            return _pipeline
        if _pipeline_init_error is not None:
            raise RuntimeError(_pipeline_init_error)

        try:
            # Heavy initialization (embedding model/data) stays off event loop.
            _pipeline = await asyncio.to_thread(DisasterRAGPipeline)
        except Exception as exc:  # pragma: no cover - depends on local model/env
            _pipeline_init_error = str(exc)
            logger.error("Failed to initialize RAG pipeline: %s", exc)
            raise
        return _pipeline


class DroneInputRequest(BaseModel):
    """Request model for drone detection"""
    latitude: float
    longitude: float
    flood_depth_cm: float
    severity: str  # "low", "medium", "high", "critical"
    affected_area_sq_km: float
    drone_id: str = "DRONE-DEFAULT"


class ShelterInfo(BaseModel):
    """Shelter information"""
    shelter_id: str
    name: str
    location: str
    distance_km: float
    available_beds: int
    total_capacity: int
    amenities: List[str]


class OperationInfo(BaseModel):
    """Historical operation information"""
    operation_id: str
    date: str
    location: str
    severity: str
    affected_population: int
    outcome: str
    lessons_learned: str


class DisasterResponseMessage(BaseModel):
    """Response from RAG system"""
    message_victim: str
    message_rescuer: str
    shelters: List[ShelterInfo]
    operations: List[OperationInfo]
    recommended_techniques: List[str]
    resources_needed: List[str]
    confidence_score: float | dict[str, str]
    query_context: dict


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "operational",
        "service": "Disaster Response RAG System",
        "endpoints": [
            "/docs - API documentation",
            "/health - Health check",
            "/process-drone - Process drone input",
            "/shelters - Get all shelters",
            "/operations - Get all operations"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Disaster Response RAG",
        "version": "1.0.0"
    }


@app.post("/process-drone", response_model=DisasterResponseMessage)
async def process_drone(request: DroneInputRequest):
    """
    Process drone input and generate disaster response
    
    Args:
        request: Drone detection data
        
    Returns:
        DisasterResponseMessage with victim and rescuer messages
    """
    try:
        logger.info(f"Processing drone request from {request.drone_id}")
        
        # Validate severity
        try:
            severity = SeverityLevel[request.severity.upper()]
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid severity. Must be: {', '.join([s.value for s in SeverityLevel])}"
            )
        
        # Create drone input
        drone_input = DroneInput(
            latitude=request.latitude,
            longitude=request.longitude,
            flood_depth_cm=request.flood_depth_cm,
            severity=severity,
            affected_area_sq_km=request.affected_area_sq_km,
            drone_id=request.drone_id
        )
        
        # Process through pipeline
        pipeline = await _get_pipeline()
        response = await pipeline.process_drone_input_async(drone_input)
        
        # Format shelters
        shelters = [
            ShelterInfo(
                shelter_id=s.shelter_id,
                name=s.name,
                location=s.location,
                distance_km=s.distance_km,
                available_beds=s.capacity - s.current_occupancy,
                total_capacity=s.capacity,
                amenities=s.amenities
            )
            for s in response.relevant_shelters
        ]
        
        # Format operations
        operations = [
            OperationInfo(
                operation_id=op.operation_id,
                date=op.date,
                location=op.location,
                severity=op.severity.value,
                affected_population=op.affected_population,
                outcome=op.outcome,
                lessons_learned=op.lessons_learned
            )
            for op in response.relevant_operations
        ]
        
        confidence_payload: float | dict[str, str]
        if isinstance(response.confidence_score, tuple):
            confidence_payload = {
                "level": str(response.confidence_score[0]),
                "reason": str(response.confidence_score[1]),
            }
        else:
            confidence_payload = float(response.confidence_score)

        return DisasterResponseMessage(
            message_victim=response.message_victim,
            message_rescuer=response.message_rescuer,
            shelters=shelters,
            operations=operations,
            recommended_techniques=response.recommended_techniques,
            resources_needed=response.resources_needed,
            confidence_score=confidence_payload,
            query_context=response.query_context
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing drone input: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )


@app.get("/shelters", response_model=List[ShelterInfo])
async def get_all_shelters():
    """Get all available shelters"""
    try:
        pipeline = await _get_pipeline()
        shelters = pipeline.vector_store.shelters
        return [
            ShelterInfo(
                shelter_id=s['shelter_id'],
                name=s['name'],
                location=s['location'],
                distance_km=0,
                available_beds=s['capacity'] - s['current_occupancy'],
                total_capacity=s['capacity'],
                amenities=s['amenities']
            )
            for s in shelters
        ]
    except Exception as e:
        logger.error(f"Error retrieving shelters: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving shelters")


@app.get("/operations", response_model=List[OperationInfo])
async def get_all_operations():
    """Get all historical operations"""
    try:
        pipeline = await _get_pipeline()
        operations = pipeline.vector_store.operations
        return [
            OperationInfo(
                operation_id=op['operation_id'],
                date=op['date'],
                location=op['location'],
                severity=op['severity'],
                affected_population=op['affected_population'],
                outcome=op['outcome'],
                lessons_learned=op['lessons_learned']
            )
            for op in operations
        ]
    except Exception as e:
        logger.error(f"Error retrieving operations: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving operations")


@app.get("/shelters/{shelter_id}")
async def get_shelter(shelter_id: str):
    """Get specific shelter by ID"""
    try:
        pipeline = await _get_pipeline()
        shelter = next(
            (s for s in pipeline.vector_store.shelters if s['shelter_id'] == shelter_id),
            None
        )
        if not shelter:
            raise HTTPException(status_code=404, detail=f"Shelter {shelter_id} not found")
        return shelter
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving shelter: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving shelter")


@app.get("/operations/{operation_id}")
async def get_operation(operation_id: str):
    """Get specific operation by ID"""
    try:
        pipeline = await _get_pipeline()
        operation = next(
            (op for op in pipeline.vector_store.operations if op['operation_id'] == operation_id),
            None
        )
        if not operation:
            raise HTTPException(status_code=404, detail=f"Operation {operation_id} not found")
        return operation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving operation: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving operation")


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Disaster Response RAG API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
