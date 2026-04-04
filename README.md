# Disaster Response RAG System - Demo

A Retrieval-Augmented Generation (RAG) system for disaster response during Mumbai floods. This system uses drone detection inputs to generate intelligent responses for both disaster victims and rescue coordinators.

## System Architecture

### Core Components

1. **Drone Input Module** (`models/drone_input.py`)
   - Receives flood detection data (latitude, longitude, depth, severity)
   - Defines data structures for shelters, operations, and responses

2. **Vector Store & Retrieval** (`rag/retriever.py`)
   - Semantic search using embeddings
   - Geographic proximity-based filtering
   - Retrieves relevant shelters and historical operations

3. **LLM Response Generation** (`rag/generator.py`)
   - Uses Groq API (Mixtral model)
   - Generates victim-focused and rescuer-focused messages
   - Recommends techniques and resources

4. **RAG Pipeline** (`rag/rag_pipeline.py`)
   - Orchestrates entire workflow
   - Combines retrieval and generation
   - Produces confidence scores

5. **Demo Database** (`database/`)
   - Mumbai shelters (5 locations)
   - Historical rescue operations (4 operations)
   - Includes amenities, techniques, resources

## Features

### For Victims
- Clear, reassuring evacuation instructions
- Nearest shelter locations with availability
- What to bring and how to prepare
- Emergency contact information

### For Rescuers
- Detailed operation plan based on historical data
- Recommended rescue techniques
- Resource allocation strategy
- Phased evacuation approach
- Medical response setup

### Intelligence Features
- Geographic proximity matching
- Semantic search on historical data
- Severity-based operation matching
- Confidence scoring
- Technique/resource recommendation from past operations

## Data Structure

### Shelters Database
- 5 demo shelters across Mumbai
- Capacity tracking
- Amenities list
- Geographic coordinates

### Operations Database
- 4 historical operations
- Techniques deployed
- Resources used
- Lessons learned
- Population impacted

## Usage

### Basic Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set Groq API key
export GROQ_API_KEY="your_groq_api_key_here"
# or edit config/settings.py
```

### Running Demo

```bash
python main.py
```

### Using as Library

```python
from models.drone_input import DroneInput, SeverityLevel
from rag.rag_pipeline import DisasterRAGPipeline

# Create drone input
drone_input = DroneInput(
    latitude=19.0596,
    longitude=72.8295,
    flood_depth_cm=120,
    severity=SeverityLevel.MEDIUM,
    affected_area_sq_km=2.5
)

# Process through RAG
pipeline = DisasterRAGPipeline()
response = pipeline.process_drone_input(drone_input)

# Access results
print(response.message_victim)
print(response.message_rescuer)
```

## Project Structure

```
disaster_rag_demo/
├── config/
│   ├── settings.py          # Configuration & constants
│   └── __init__.py
├── database/
│   ├── db_init.py          # Demo data initialization
│   └── __init__.py
├── models/
│   ├── drone_input.py      # Data models
│   └── __init__.py
├── rag/
│   ├── retriever.py        # Vector store & retrieval
│   ├── generator.py        # LLM response generation
│   ├── rag_pipeline.py     # Main pipeline
│   └── __init__.py
├── utils/
│   ├── embeddings.py       # Text embedding utilities
│   ├── text_processing.py  # Text formatting & processing
│   ├── logger.py          # Logging utility
│   └── __init__.py
├── main.py                 # Demo entry point
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## Configuration

Edit `config/settings.py` to customize:
- Groq API key and model
- Embedding model
- Search parameters (top_k, similarity threshold)
- Mumbai boundaries
- Message types and paths

## Demo Scenarios

### Scenario 1: Moderate Flood (Bandra)
- Flood depth: 120 cm
- Severity: Medium
- Affected area: 2.5 sq km

### Scenario 2: Critical Flood (Dharavi)
- Flood depth: 250 cm
- Severity: Critical
- Affected area: 5.8 sq km

### Scenario 3: High Flood (Eastern Suburbs)
- Flood depth: 180 cm
- Severity: High
- Affected area: 4.2 sq km

## Output

Each scenario produces:
1. **Victim Message**: Clear evacuation instructions and shelter info
2. **Rescuer Plan**: Detailed operation strategy with techniques and resources
3. **Shelter Recommendations**: Relevant shelters with availability
4. **Historical Context**: Relevant past operations
5. **Confidence Score**: Reliability of recommendations

## Extending the System

### Add More Shelters
Edit `database/db_init.py`, add to `create_shelters_data()`

### Add More Historical Data
Edit `database/db_init.py`, add to `create_rescue_operations_data()`

### Modify LLM Behavior
Edit `rag/generator.py`, customize prompts in `generate_victim_message()` and `generate_rescuer_plan()`

### Change Search Parameters
Edit `config/settings.py`, adjust `TOP_K_RESULTS`, `CONFIDENCE_THRESHOLD`, etc.

## Logging

Logs are saved to `logs/disaster_rag.log` with full debug information.

## Dependencies

- **groq**: LLM API client
- **sentence-transformers**: Text embeddings
- **scikit-learn**: Similarity calculations
- **numpy**: Numerical operations
- **python-dotenv**: Environment variable management

## Notes

- This is a demo system for educational purposes
- Uses sample data for Mumbai floods
- Requires Groq API key (free tier available)
- Customizable for other disaster types and locations

## Future Enhancements

- Real-time data integration
- Multi-language support
- SMS/WhatsApp victim alerts
- Real-time resource tracking
- Mobile app integration
- Video feed analysis from drones
