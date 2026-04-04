"""
Initialize demo database with Mumbai flood data
"""
import json
from pathlib import Path
from models.drone_input import Shelter, RescueOperation, SeverityLevel


def create_shelters_data():
    """Create demo shelter data for Mumbai"""
    shelters = [
        {
            "shelter_id": "SHELTER-001",
            "name": "Bandra High School",
            "location": "Bandra, West",
            "latitude": 19.0596,
            "longitude": 72.8295,
            "capacity": 500,
            "current_occupancy": 250,
            "amenities": ["Medical Facility", "Food & Water", "Sanitation", "Electricity", "Cots"],
            "contact": "+91-22-XXXX-0001"
        },
        {
            "shelter_id": "SHELTER-002",
            "name": "Worli Sports Complex",
            "location": "Worli",
            "latitude": 19.0176,
            "longitude": 72.8194,
            "capacity": 800,
            "current_occupancy": 450,
            "amenities": ["Medical Facility", "Food & Water", "Sanitation", "Electricity", "Cots", "WiFi"],
            "contact": "+91-22-XXXX-0002"
        },
        {
            "shelter_id": "SHELTER-003",
            "name": "Fort Community Center",
            "location": "Fort",
            "latitude": 18.9678,
            "longitude": 72.8226,
            "capacity": 600,
            "current_occupancy": 350,
            "amenities": ["Medical Facility", "Food & Water", "Sanitation", "Electricity", "Cots", "Children Area"],
            "contact": "+91-22-XXXX-0003"
        },
        {
            "shelter_id": "SHELTER-004",
            "name": "Mulund Community Hall",
            "location": "Mulund East",
            "latitude": 19.1619,
            "longitude": 72.9520,
            "capacity": 400,
            "current_occupancy": 180,
            "amenities": ["Medical Facility", "Food & Water", "Sanitation", "Electricity", "Cots"],
            "contact": "+91-22-XXXX-0004"
        },
        {
            "shelter_id": "SHELTER-005",
            "name": "Dharavi Temporary Relief Center",
            "location": "Dharavi",
            "latitude": 19.0176,
            "longitude": 72.8677,
            "capacity": 1000,
            "current_occupancy": 680,
            "amenities": ["Medical Facility", "Food & Water", "Sanitation", "Electricity", "Cots", "Mobile Clinic"],
            "contact": "+91-22-XXXX-0005"
        }
    ]
    return shelters


def create_rescue_operations_data():
    """Create demo rescue operation data from previous Mumbai floods"""
    operations = [
        {
            "operation_id": "OP-2022-001",
            "date": "2022-07-15",
            "location": "Bandra-Worli Area",
            "latitude": 19.0400,
            "longitude": 72.8250,
            "severity": "high",
            "affected_population": 5000,
            "techniques_used": [
                "Rubber Boat Rescue",
                "Swimming Team Rescue",
                "Helicopter Evacuation",
                "Rope Rescue",
                "Amphibious Vehicles"
            ],
            "resources_deployed": [
                "20 Rubber Boats",
                "5 NDRF Teams",
                "2 Helicopters",
                "50 Rescue Personnel",
                "10 Ambulances",
                "3 First Aid Camps"
            ],
            "shelters_activated": ["SHELTER-001", "SHELTER-002", "SHELTER-003"],
            "duration_hours": 36,
            "outcome": "All 5000 residents evacuated successfully",
            "lessons_learned": "Early warning system deployment crucial. Pre-positioned boats reduce response time by 50%. Trained swimmers needed in every team."
        },
        {
            "operation_id": "OP-2021-005",
            "date": "2021-08-20",
            "location": "Dharavi-Mahim Area",
            "latitude": 19.0180,
            "longitude": 72.8550,
            "severity": "critical",
            "affected_population": 8000,
            "techniques_used": [
                "High-Speed Rescue Boats",
                "Helicopter Evacuation",
                "Door-to-Door Rescue",
                "Wading Rescue",
                "Swimming Rescue"
            ],
            "resources_deployed": [
                "30 Boats",
                "8 NDRF Teams",
                "3 Helicopters",
                "100 Rescue Personnel",
                "15 Ambulances",
                "5 Medical Camps"
            ],
            "shelters_activated": ["SHELTER-005", "SHELTER-002"],
            "duration_hours": 48,
            "outcome": "8000 residents evacuated, 50 medical emergencies handled",
            "lessons_learned": "Elderly and disabled require special attention and equipment. Pre-positioned medical supplies save lives. Communication channels must be robust."
        },
        {
            "operation_id": "OP-2023-003",
            "date": "2023-06-10",
            "location": "Eastern Suburbs",
            "latitude": 19.1500,
            "longitude": 72.9300,
            "severity": "medium",
            "affected_population": 3000,
            "techniques_used": [
                "Manual Wading",
                "Rope Lines",
                "Boat Shuttle Service",
                "Swimming Rescue"
            ],
            "resources_deployed": [
                "10 Boats",
                "3 NDRF Teams",
                "30 Rescue Personnel",
                "5 Ambulances",
                "2 Medical Camps"
            ],
            "shelters_activated": ["SHELTER-004"],
            "duration_hours": 18,
            "outcome": "3000 residents evacuated safely in 18 hours",
            "lessons_learned": "Early evacuation reduces chaos. Local volunteer networks accelerate response. Pre-training residents saves rescue time."
        },
        {
            "operation_id": "OP-2020-008",
            "date": "2020-09-05",
            "location": "South Mumbai (Fort-Colaba)",
            "latitude": 18.9580,
            "longitude": 72.8300,
            "severity": "high",
            "affected_population": 4500,
            "techniques_used": [
                "High-Speed Rescue Boats",
                "Building Rappelling",
                "Helicopter Rescue",
                "Amphibious Vehicles",
                "Swimming Rescue Teams"
            ],
            "resources_deployed": [
                "25 Boats",
                "6 NDRF Teams",
                "2 Helicopters",
                "60 Rescue Personnel",
                "10 Ambulances",
                "4 Medical Camps"
            ],
            "shelters_activated": ["SHELTER-003", "SHELTER-002"],
            "duration_hours": 40,
            "outcome": "4500 residents rescued, zero casualties",
            "lessons_learned": "Building heights require specialized rope rescue training. Helicopter availability crucial for critical cases. Medical triage systems effective."
        }
    ]
    return operations


def initialize_database():
    """Initialize all demo data files"""
    db_path = Path("database/demo_data")
    db_path.mkdir(parents=True, exist_ok=True)
    
    # Create shelters file
    shelters = create_shelters_data()
    shelters_file = db_path / "shelters_mumbai.json"
    with open(shelters_file, 'w') as f:
        json.dump(shelters, f, indent=2)
    print(f"✓ Created shelters database: {shelters_file}")
    
    # Create operations file
    operations = create_rescue_operations_data()
    operations_file = db_path / "rescue_operations_mumbai.json"
    with open(operations_file, 'w') as f:
        json.dump(operations, f, indent=2)
    print(f"✓ Created rescue operations database: {operations_file}")
    
    return shelters_file, operations_file


def load_shelters():
    """Load shelters from database"""
    shelters_file = Path("database/demo_data/shelters_mumbai.json")
    if not shelters_file.exists():
        print("Database not initialized. Running initialization...")
        initialize_database()
    
    with open(shelters_file, 'r') as f:
        data = json.load(f)
    return data


def load_rescue_operations():
    """Load rescue operations from database"""
    operations_file = Path("database/demo_data/rescue_operations_mumbai.json")
    if not operations_file.exists():
        print("Database not initialized. Running initialization...")
        initialize_database()
    
    with open(operations_file, 'r') as f:
        data = json.load(f)
    return data


if __name__ == "__main__":
    initialize_database()
    print("\n✓ Database initialization completed!")
