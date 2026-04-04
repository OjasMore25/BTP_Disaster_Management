"""
FastAPI service for Disaster Response RAG System
Provides REST endpoints for drone input and response generation
"""
try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    from typing import List
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

from models.drone_input import DroneInput, SeverityLevel
from rag.rag_pipeline import DisasterRAGPipeline
from utils.logger import get_logger

if not HAS_FASTAPI:
    raise ImportError("FastAPI not installed. Install with: pip install fastapi uvicorn")

logger = get_logger()
app = FastAPI(
    title="Disaster Response RAG API",
    description="RAG system for flood disaster response",
    version="1.0.0"
)

# Initialize pipeline (single instance for performance)
pipeline = DisasterRAGPipeline()


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
    confidence_score: float
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
        response = pipeline.process_drone_input(drone_input)
        
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
        
        return DisasterResponseMessage(
            message_victim=response.message_victim,
            message_rescuer=response.message_rescuer,
            shelters=shelters,
            operations=operations,
            recommended_techniques=response.recommended_techniques,
            resources_needed=response.resources_needed,
            confidence_score=response.confidence_score,
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
