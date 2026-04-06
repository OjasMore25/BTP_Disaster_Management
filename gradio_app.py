"""
Gradio Web UI for Disaster Response RAG System
Provides an interactive interface for drone input and disaster response
"""

import gradio as gr
import json
from datetime import datetime

from rag.models.drone_input import DroneInput, SeverityLevel
from rag.rag.rag_pipeline import DisasterRAGPipeline
from rag.utils.logger import Logger

# Initialize logger
logger = Logger()

# Initialize RAG Pipeline
try:
    rag_pipeline = DisasterRAGPipeline()
    logger.info("RAG Pipeline initialized for Gradio UI")
except Exception as e:
    logger.error(f"Failed to initialize RAG Pipeline: {str(e)}")
    rag_pipeline = None


def process_disaster_input(latitude, longitude, flood_depth_cm, severity, affected_area, drone_id="DRONE-UI-001"):
    """
    Process disaster input and return RAG response
    
    Args:
        latitude: Disaster location latitude
        longitude: Disaster location longitude
        flood_depth_cm: Flood depth in centimeters
        severity: Severity level (LOW, MEDIUM, HIGH, CRITICAL)
        affected_area: Affected area in square kilometers
        drone_id: Optional drone identifier
    
    Returns:
        Tuple of 8 values for Gradio output components
    """
    
    if rag_pipeline is None:
        return ("System unavailable", "System unavailable", "N/A", 0, 0, 
                "N/A", "N/A", "RAG Pipeline not initialized. Check GROQ_API_KEY.")
    
    try:
        # Validate inputs
        try:
            lat = float(latitude)
            lon = float(longitude)
            depth = float(flood_depth_cm)
            area = float(affected_area)
        except ValueError as e:
            return ("", "", "0%", 0, 0, "", severity.upper(), 
                   f"Invalid numeric input: {str(e)}")
        
        # Create drone input with datetime object
        from datetime import datetime as dt
        drone_input = DroneInput(
            latitude=lat,
            longitude=lon,
            flood_depth_cm=depth,
            severity=SeverityLevel[severity.upper()],
            affected_area_sq_km=area,
            timestamp=dt.now(),
            drone_id=drone_id
        )
        
        # Process through RAG pipeline
        response = rag_pipeline.process_drone_input(drone_input)
        
        # Return 8 values for 8 output components
        logger.info(f"Successfully processed UI request: {drone_id}")
        # Format confidence (handle both tuple and float)
        if isinstance(response.confidence_score, tuple):
            conf_level, conf_reason = response.confidence_score
            confidence_display = f"{conf_level} - {conf_reason}"
        else:
            confidence_display = f"{response.confidence_score:.1%}"
        
        return (
            response.message_victim,                    # victim_output
            response.message_rescuer,                   # rescuer_output
            confidence_display,                         # confidence
            float(len(response.relevant_shelters)),     # shelters_count
            float(len(response.relevant_operations)),   # operations_count
            f"{lat}, {lon}",                            # location_display
            severity.upper(),                           # severity_display
            "✓ Processing complete"                     # error_display
        )
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        logger.error(error_msg)
        return ("Failed to generate response", "Failed to generate response", "0%", 0, 0, 
                "", severity.upper(), error_msg)


def format_shelters_display(latitude, longitude):
    """Display nearby shelters for given location"""
    if rag_pipeline is None:
        return "System not initialized"
    
    try:
        lat = float(latitude)
        lon = float(longitude)
        shelters = rag_pipeline.vector_store.retrieve_shelters(lat, lon, "flood shelter", top_k=5)
        
        if not shelters:
            return "No shelters found in database"
        
        output = "### Nearby Shelters\n\n"
        for idx, shelter in enumerate(shelters, 1):
            output += f"**{idx}. {shelter['name']}**\n"
            output += f"- Location: {shelter['location']}\n"
            output += f"- Capacity: {shelter['capacity']} people\n"
            output += f"- Available Beds: {shelter['capacity'] - shelter['current_occupancy']}\n"
            output += f"- Distance: {shelter.get('distance_km', 'N/A')} km\n"
            output += f"- Amenities: {', '.join(shelter['amenities'])}\n"
            output += f"- Contact: {shelter['contact']}\n\n"
        
        return output
    except Exception as e:
        return f"Error fetching shelters: {str(e)}"


def get_example_scenarios():
    """Return example disaster scenarios"""
    return json.dumps({
        "examples": [
            {
                "name": "Moderate Flood - Bandra",
                "latitude": 19.0596,
                "longitude": 72.8295,
                "depth": 120,
                "severity": "MEDIUM",
                "area": 2.5
            },
            {
                "name": "Critical Flood - Dharavi",
                "latitude": 19.018,
                "longitude": 72.855,
                "depth": 250,
                "severity": "CRITICAL",
                "area": 5.8
            },
            {
                "name": "High Flood - Eastern Suburbs",
                "latitude": 19.15,
                "longitude": 72.93,
                "depth": 180,
                "severity": "HIGH",
                "area": 4.2
            }
        ]
    }, indent=2)


# Create Gradio Interface
with gr.Blocks(title="Disaster Response RAG System", theme=gr.themes.Soft()) as demo:
    
    gr.Markdown("""
    # 🌊 Mumbai Disaster Response RAG System
    
    **Intelligent disaster response assistant powered by AI**
    
    Enter drone detection data to receive:
    - 📢 Clear evacuation messages for disaster victims
    - 📋 Strategic operation plans for rescue coordinators
    - 🏘️ Shelter recommendations based on location
    - 📊 Historical operation insights and techniques
    
    *System uses semantic search + Groq LLM to generate contextual responses*
    """)
    
    with gr.Tabs():
        # Tab 1: Main Processing
        with gr.Tab("🚁 Drone Detection Input"):
            gr.Markdown("### Enter Drone Detection Data")
            
            with gr.Row():
                latitude = gr.Number(label="Latitude", value=19.0596, step=0.0001)
                longitude = gr.Number(label="Longitude", value=72.8295, step=0.0001)
            
            with gr.Row():
                flood_depth = gr.Number(label="Flood Depth (cm)", value=120, minimum=1, step=1)
                severity = gr.Dropdown(
                    choices=["LOW", "MEDIUM", "HIGH", "CRITICAL"],
                    value="MEDIUM",
                    label="Severity Level"
                )
            
            affected_area = gr.Number(label="Affected Area (sq km)", value=2.5, minimum=0.1, step=0.1)
            drone_id = gr.Textbox(label="Drone ID (optional)", value="DRONE-UI-001", lines=1)
            
            submit_btn = gr.Button("🔍 Process Disaster Input", variant="primary", size="lg")
            
            gr.Markdown("---")
            gr.Markdown("### Response Output")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### 👥 For Disaster Victims")
                    victim_output = gr.Textbox(
                        label="Evacuation Message",
                        lines=12,
                        interactive=False
                    )
                
                with gr.Column():
                    gr.Markdown("#### 👮 For Rescue Coordinators")
                    rescuer_output = gr.Textbox(
                        label="Operation Plan",
                        lines=12,
                        interactive=False
                    )
            
            with gr.Row():
                confidence = gr.Textbox(label="Confidence Score", interactive=False)
                shelters_count = gr.Number(label="Shelters Found", interactive=False)
                operations_count = gr.Number(label="Historical Ops", interactive=False)
            
            with gr.Row():
                location_display = gr.Textbox(label="Location", interactive=False)
                severity_display = gr.Textbox(label="Severity", interactive=False)
            
            error_display = gr.Textbox(label="Messages", interactive=False, visible=True)
            
            # Connect submit button
            submit_btn.click(
                fn=process_disaster_input,
                inputs=[latitude, longitude, flood_depth, severity, affected_area, drone_id],
                outputs=[victim_output, rescuer_output, confidence, shelters_count, 
                        operations_count, location_display, severity_display, error_display]
            )
        
        # Tab 2: Shelter Explorer
        with gr.Tab("🏘️ Shelter Explorer"):
            gr.Markdown("### Find Nearby Shelters")
            gr.Markdown("*Enter coordinates to see available shelters in that area*")
            
            with gr.Row():
                shelter_lat = gr.Number(label="Latitude", value=19.0596, step=0.0001)
                shelter_lon = gr.Number(label="Longitude", value=72.8295, step=0.0001)
            
            find_shelters_btn = gr.Button("🔍 Find Shelters", variant="primary")
            shelters_output = gr.Markdown()
            
            find_shelters_btn.click(
                fn=format_shelters_display,
                inputs=[shelter_lat, shelter_lon],
                outputs=shelters_output
            )
        
        # Tab 3: Examples
        with gr.Tab("📋 Example Scenarios"):
            gr.Markdown("### Pre-configured Test Scenarios")
            gr.Markdown("*Click on any scenario to fill in the values*")
            
            scenarios = get_example_scenarios()
            examples_display = gr.JSON(value=json.loads(scenarios), label="Available Scenarios")
            
            gr.Markdown("""
            ### Quick Test Guide
            
            1. **Moderate Flood (Bandra)**: 19.0596, 72.8295 - 120cm depth, MEDIUM severity
            2. **Critical Flood (Dharavi)**: 19.018, 72.855 - 250cm depth, CRITICAL severity
            3. **High Flood (Eastern Suburbs)**: 19.15, 72.93 - 180cm depth, HIGH severity
            
            Copy coordinates and paste in the main tab to test.
            """)
        
        # Tab 4: System Info
        with gr.Tab("ℹ️ System Information"):
            gr.Markdown("""
            ## Disaster Response RAG System
            
            ### What is this?
            An AI-powered system that:
            - **Detects** flood disasters via drone input (lat/lon/depth)
            - **Retrieves** relevant shelters and historical operations using semantic search
            - **Generates** two types of messages using LLM:
              - **Victim Message**: Clear, actionable evacuation instructions
              - **Rescuer Plan**: Strategic operation guidelines for rescue teams
            
            ### How it works
            1. **Input**: Drone detects flood (location, depth, severity, area)
            2. **Retrieval**: Semantic search finds:
               - Nearby shelters (70% semantic + 30% geographic distance)
               - Historical similar operations (for reference)
            3. **Generation**: LLM creates context-aware messages
            4. **Output**: Two formatted messages + metadata
            
            ### Key Features
            - ✅ Modular RAG architecture
            - ✅ Semantic search with embeddings (sentence-transformers)
            - ✅ Geographic proximity matching (Haversine formula)
            - ✅ LLM generation via Groq API (llama-3.1-70b-versatile)
            - ✅ Fallback responses when API unavailable
            - ✅ 5 shelters + 4 historical operations in demo database
            
            ### Mumbai Coverage
            - Geographic bounds: 18.90°N to 19.25°N, 72.70°E to 73.05°E
            - Shelters: Bandra, Worli, Fort, Mulund, Dharavi
            - Historical operations: 2020-2023
            
            ### API Requirements
            - **Groq API Key**: Required (set in .env file)
            - **Model**: llama-3.1-70b-versatile (active model)
            - **Rate limits**: Check Groq console for limits
            
            ### Logs & Debug
            - Log file: `logs/disaster_rag.log`
            - Console output shows all processing steps
            - Errors logged with full traceback
            """)
    
    gr.Markdown("""
    ---
    **Built with**: Python • Groq API • Sentence-Transformers • Gradio
    
    **Warning**: Model `mixtral-8x7b-32768` was decommissioned. Now using `llama-3.1-70b-versatile`
    """)


if __name__ == "__main__":
    # Launch on localhost
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        debug=True
    )
