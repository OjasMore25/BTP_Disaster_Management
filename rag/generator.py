"""
LLM response generation using Groq API
"""
from typing import Dict, Tuple
from groq import Groq
from config.settings import GROQ_API_KEY, GROQ_MODEL, TEMPERATURE
from utils.logger import get_logger

logger = get_logger()


class DisasterResponseGenerator:
    """Generate responses for disaster victims and rescuers using Groq API"""
    
    def __init__(self):
        """Initialize Groq client"""
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = GROQ_MODEL
        self.temperature = TEMPERATURE
        logger.info(f"Initialized Groq client with model: {self.model}")
    
    def generate_victim_message(self, context: str, shelters_info: str) -> str:
        """
        Generate reassuring message for flood victims
        
        Args:
            context: Drone and flood information
            shelters_info: Available shelters information
            
        Returns:
            Message for victims (3 bullets max, <50 words)
        """
        prompt = f"""EMERGENCY ALERT FOR FLOOD VICTIMS - EXTREME BREVITY REQUIRED

SITUATION:
{context}

SHELTERS (sorted by closest + available capacity, top 3 only):
{shelters_info}

Generate a MAXIMUM 3-BULLET alert:
• ONE line: Where to go RIGHT NOW (specific location, distance)
• ONE line: What to do (simple verb, no explanation)
• ONE line: Call this number if trapped

Constraints:
- MAXIMUM 50 words total
- Zero analysis, zero paragraphs, zero explanations
- Simple verbs only (Go, Call, Move, Bring)
- Assume low battery, panic, non-native English speaker
- Must be readable in 5 seconds

START ALERT (bullets only):"""

        try:
            message = self.client.chat.completions.create(
                model=self.model,
                max_tokens=400,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            response = message.choices[0].message.content
            
            # Remove thinking tags and clean response
            response = self._clean_response(response)
            
            logger.info("Generated victim message successfully")
            return response
        
        except Exception as e:
            logger.error(f"Error generating victim message: {str(e)}")
            return self._fallback_victim_message(context, shelters_info)
    
    def generate_rescuer_plan(self, context: str, operations_info: str, 
                             techniques: str, resources: str, weather_data: str = "") -> str:
        """
        Generate rescue operation plan for rescuers
        
        Args:
            context: Drone and flood information
            operations_info: Historical rescue operations
            techniques: Recommended techniques
            resources: Available resources (must be deduplicated: Deployed vs Standby)
            weather_data: Current weather (monsoon check, visibility, wind)
            
        Returns:
            Detailed rescue plan with risk flags and offline fallbacks
        """
        prompt = f"""RESCUE OPERATION PLAN FOR MUMBAI FLOOD - REAL CONDITIONS

CURRENT SITUATION:
{context}

WEATHER CONDITIONS (critical for helicopter/boat ops):
{weather_data if weather_data else 'Monsoon season - assume high wind, low visibility, rotor wash risk'}

HISTORICAL OPERATIONS REFERENCE:
{operations_info}

RECOMMENDED TECHNIQUES:
{techniques}

AVAILABLE RESOURCES (deduplicated, categorized):
{resources}

Create EXECUTABLE rescue plan with:

1. IMMEDIATE PRIORITIES (0-2 hours, ground-based only if weather risk):
   - Specific locations, team sizes, equipment
   - FLAG: Any helicopter ops only if visibility >500m, wind <25 knots

2. PHASED EVACUATION:
   - Priority: elderly, disabled, children first
   - Route safety checks
   - Assembly points with headcount procedures

3. RESOURCES:
   - Show DEPLOYED NOW vs ON STANDBY (don't mix)
   - Equipment per team (boats, life jackets, radios)
   - Medical camp setup (location, staff, supplies)

4. OFFLINE FALLBACKS (power/network down):
   - SMS alternatives if network dead
   - Police/volunteer runner coordination
   - Manual headcount procedures
   - Local amplified announcements

5. WEATHER CONTINGENCIES:
   - What changes if wind >25 knots
   - When to halt helicopter deployment
   - Boat safety limits

Be specific, operational, executable. Assume officer is tired, weather is bad, network may fail.

RESCUE OPERATION PLAN:"""

        try:
            message = self.client.chat.completions.create(
                model=self.model,
                max_tokens=1000,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            response = message.choices[0].message.content
            
            # Remove thinking tags and clean response
            response = self._clean_response(response)
            
            logger.info("Generated rescuer plan successfully")
            return response
        
        except Exception as e:
            logger.error(f"Error generating rescuer plan: {str(e)}")
            return self._fallback_rescuer_plan(context, techniques)
    
    def _clean_response(self, response: str) -> str:
        """
        Clean response by removing thinking blocks at the start
        
        Args:
            response: Raw model response
            
        Returns:
            Cleaned response
        """
        import re
        
        # Remove <think>...</think> blocks entirely
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL | re.IGNORECASE)
        
        # Also handle unclosed think tags by removing everything before meaningful content
        if '<think>' in response.lower():
            # Find where the think block ends
            parts = re.split(r'</think>', response, flags=re.IGNORECASE)
            if len(parts) > 1:
                response = parts[-1]
        
        # Find the actual content - look for section markers or operational keywords
        operational_markers = [
            '**URGENT',
            '**RESCUE',
            '**EMERGENCY',
            '**OPERATION',
            '###',  # Markdown headers
            '##',  # Markdown headers
            'IMMEDIATE',
            'Bandra',  # Location names
            'Dharavi',
            'Deploy',
            'Move to higher'
        ]
        
        lines = response.split('\n')
        
        # Find first line with actual content (not reasoning)
        for i, line in enumerate(lines):
            if any(marker in line for marker in operational_markers):
                response = '\n'.join(lines[i:])
                break
        
        # Clean up excessive newlines
        response = re.sub(r'\n\n\n+', '\n\n', response)
        response = response.strip()
        
        return response if response.strip() else "(Response generation incomplete)"
    
    def _fallback_victim_message(self, context: str, shelters_info: str) -> str:
        """Fallback message for victims if API fails - 3 bullets ONLY"""
        return f"""FLOOD ALERT - MOVE NOW

• Go to higher ground: Nearest shelter {shelters_info.split('km')[0]}km away
• Call 112 if trapped
• Bring: Phone, ID, medicines only
"""
    
    def _fallback_rescuer_plan(self, context: str, techniques: str) -> str:
        """Fallback plan for rescuers if API fails - offline-first, resource-clear"""
        return f"""RESCUE OPERATION PLAN - MUMBAI FLOOD (OFFLINE-CAPABLE)

CURRENT SITUATION:
{context}

WEATHER RISK: Monsoon conditions - helicopters flagged HIGH RISK. Use ground/boats first.

IMMEDIATE (0-2 hours, assume network DOWN):
1. Assessment teams: 3 boats to Dharavi, Bandra, Mulund (with portable radios)
2. Police runners to announce shelter locations (Bandra High School = primary)
3. Medical camps: Dharavi (50-bed), Bandra (100-bed), Mulund (50-bed)
4. Manual headcount at shelters using paper forms + SMS batch reporting

EVACUATION PRIORITY:
1. Children, elderly, disabled (ages 0-5, 65+, mobility limited)
2. Use {techniques}
3. Assembly points: Bandra High School (main), Mulund Community Center (overflow)
4. Headcount tracking: Paper tally → digital batch sync when network restored

RESOURCES DEPLOYED NOW:
- 4 rescue boats (manned, with life jackets + medical kits)
- 8 ambulances (Dharavi 3, Bandra 3, Mulund 2)
- 2 medical teams (doctors + nurses)
- Police + volunteers (coordination only, no assets)

RESOURCES ON STANDBY (activate if needed):
- 2 helicopters (deploy ONLY if: visibility >500m, wind <25 knots, no rotor wash risk)
- 6 additional boats (if water levels spike >1.5m)
- Additional medical camps (if casualty count >300)

OFFLINE COORDINATION (if SMS/network down):
- Police runners between command center and shelters
- Loudspeaker announcements from police vans
- Manual log sheets (time, location, headcount, medical needs)
- Batch SMS when network restored

WEATHER CHECKPOINTS:
- Check wind every 30min: >25 knots = halt helicopter ops
- Check visibility: <500m = boats move closer to shore only
- Rooftop ops: allowed only if rotor wash won't endanger crowd

ONGOING:
- Monitor water levels + weather every 30 minutes
- Adjust boat routes if depth changes
- Update shelter occupancy manually, sync digital logs when possible
- Communication: radios + runners (primary), SMS when network allows"""
    
    def calculate_confidence(self, relevant_results: int, query_quality: str) -> Tuple[str, str]:
        """
        Calculate operationally meaningful confidence assessment
        
        Args:
            relevant_results: Number of relevant historical results found
            query_quality: Quality of the search (high/medium/low)
            
        Returns:
            Tuple of (confidence_level, brief_reason)
            - confidence_level: 'HIGH', 'MEDIUM', or 'LOW'
            - brief_reason: Why (e.g., '5+ similar ops, clear patterns' or 'Limited historical data')
        """
        # Decision logic: confidence based on DATA RICHNESS + PATTERN CLARITY
        # Not pseudo-precise percentages
        
        if relevant_results >= 5 and query_quality == "high":
            return ("HIGH", "5+ similar ops, clear evacuation patterns")
        elif relevant_results >= 3 and query_quality in ["high", "medium"]:
            return ("HIGH", "3+ ops match, consistent shelter routing")
        elif relevant_results >= 2 or query_quality == "high":
            return ("MEDIUM", "2+ ref ops, verify local conditions")
        elif query_quality == "medium":
            return ("MEDIUM", "Moderate data, officer discretion advised")
        else:
            return ("LOW", "Limited historical match, adapt template to local conditions")
