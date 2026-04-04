"""
Text processing utilities
"""
import re
from typing import List, Dict
import json


def clean_text(text: str) -> str:
    """
    Clean and normalize text
    
    Args:
        text: Raw text
        
    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove special characters except common punctuation
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return text


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into chunks for processing
    
    Args:
        text: Text to chunk
        chunk_size: Size of each chunk
        overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    
    return chunks


def format_shelter_context(shelter: Dict) -> str:
    """
    Format shelter data into readable context
    
    Args:
        shelter: Shelter dictionary
        
    Returns:
        Formatted string
    """
    return f"""
Shelter: {shelter['name']} ({shelter['shelter_id']})
Location: {shelter['location']}
Capacity: {shelter['capacity']} people
Current Occupancy: {shelter['current_occupancy']}
Available Beds: {shelter['capacity'] - shelter['current_occupancy']}
Amenities: {', '.join(shelter['amenities'])}
Contact: {shelter.get('contact', 'N/A')}
Distance: {shelter.get('distance_km', 'N/A')} km
"""


def format_operation_context(operation: Dict) -> str:
    """
    Format rescue operation data into readable context
    
    Args:
        operation: Operation dictionary
        
    Returns:
        Formatted string
    """
    return f"""
Operation ID: {operation['operation_id']}
Date: {operation['date']}
Location: {operation['location']}
Severity: {operation['severity'].upper()}
Affected Population: {operation['affected_population']}
Duration: {operation['duration_hours']} hours
Techniques Used: {', '.join(operation['techniques_used'])}
Resources Deployed: {', '.join(operation['resources_deployed'])}
Shelters Activated: {', '.join(operation['shelters_activated'])}
Outcome: {operation['outcome']}
Lessons Learned: {operation['lessons_learned']}
"""


def format_drone_input(drone_data: Dict) -> str:
    """
    Format drone input into readable context
    
    Args:
        drone_data: Drone input dictionary
        
    Returns:
        Formatted string
    """
    return f"""
Drone Report (ID: {drone_data['drone_id']})
Timestamp: {drone_data['timestamp']}
Location: {drone_data['latitude']:.4f}, {drone_data['longitude']:.4f}
Flood Depth: {drone_data['flood_depth_cm']} cm
Severity: {drone_data['severity'].upper()}
Affected Area: {drone_data['affected_area_sq_km']} sq km
"""


def merge_contexts(*contexts: str) -> str:
    """
    Merge multiple context strings
    
    Args:
        *contexts: Variable number of context strings
        
    Returns:
        Merged context
    """
    return "\n".join(contexts)


def extract_key_terms(text: str) -> List[str]:
    """
    Extract key terms from text
    
    Args:
        text: Input text
        
    Returns:
        List of key terms
    """
    # Simple keyword extraction
    keywords = []
    # Remove common words
    common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
    
    words = text.lower().split()
    for word in words:
        word_clean = word.strip('.,!?')
        if len(word_clean) > 3 and word_clean not in common_words:
            keywords.append(word_clean)
    
    return list(set(keywords))
