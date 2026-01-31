import httpx
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from app.config import settings


class Message(BaseModel):
    """Chat message."""
    role: str  # "system", "user", "assistant"
    content: str


class GrokResponse(BaseModel):
    """Grok API response."""
    content: str
    model: str
    usage: Dict[str, int]


class GrokClient:
    """
    Grok AI client for the Rolling Decision Engine.
    
    Used for:
    - Analyzing mission context
    - Generating route recommendations
    - Evaluating backhaul opportunities
    - Risk assessment explanations
    """
    
    def __init__(self):
        self.api_key = settings.GROK_API_KEY
        self.base_url = settings.GROK_BASE_URL
        self.model = settings.GROK_MODEL
        self.max_tokens = settings.GROK_MAX_TOKENS
        self.temperature = settings.GROK_TEMPERATURE
        
        if not self.api_key:
            raise ValueError("GROK_API_KEY not configured")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    async def chat(
        self,
        messages: List[Message],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> GrokResponse:
        """
        Send chat completion request to Grok.
        
        Args:
            messages: List of chat messages
            max_tokens: Override default max tokens
            temperature: Override default temperature
            
        Returns:
            GrokResponse with generated content
        """
        payload = {
            "model": self.model,
            "messages": [m.model_dump() for m in messages],
            "max_tokens": max_tokens or self.max_tokens,
            "temperature": temperature or self.temperature,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._get_headers(),
                json=payload,
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
        
        return GrokResponse(
            content=data["choices"][0]["message"]["content"],
            model=data["model"],
            usage=data.get("usage", {}),
        )
    
    async def analyze_mission(
        self,
        origin: str,
        destination: str,
        cargo_type: str,
        weight_tons: float,
        vehicle_type: str,
    ) -> Dict[str, Any]:
        """
        Analyze mission and provide recommendations.
        
        Module 1: Context-Aware Mission Planner
        """
        system_prompt = """You are an AI logistics expert for Indian road freight.
Analyze the mission and provide:
1. Route recommendations considering Indian highways
2. Risk factors (weather, traffic, road conditions)
3. Estimated delays at toll plazas and checkpoints
4. Fuel stop recommendations
5. Best departure time

Respond in JSON format with keys: route_advice, risks, estimated_delays, fuel_stops, best_departure"""

        user_prompt = f"""Analyze this freight mission:
- Origin: {origin}
- Destination: {destination}
- Cargo: {cargo_type}
- Weight: {weight_tons} tons
- Vehicle: {vehicle_type}"""

        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=user_prompt),
        ]
        
        response = await self.chat(messages, temperature=0.3)
        
        # Parse JSON response
        import json
        try:
            return json.loads(response.content)
        except:
            return {"raw_response": response.content}
    
    async def evaluate_opportunity(
        self,
        mission_context: Dict[str, Any],
        opportunity: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Evaluate a detected opportunity.
        
        Module 2: Rolling Decision Engine
        """
        system_prompt = """You are an AI decision engine for freight logistics.
Evaluate the opportunity and provide:
1. Should the driver accept? (yes/no/maybe)
2. Confidence score (0-100)
3. Key benefits
4. Key risks
5. Recommended action

Respond in JSON format with keys: recommendation, confidence, benefits, risks, action"""

        user_prompt = f"""Current Mission:
{mission_context}

Detected Opportunity:
{opportunity}

Should the driver take this opportunity?"""

        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=user_prompt),
        ]
        
        response = await self.chat(messages, temperature=0.2)
        
        import json
        try:
            return json.loads(response.content)
        except:
            return {"raw_response": response.content}
    
    async def suggest_backhaul(
        self,
        current_location: str,
        destination: str,
        vehicle_capacity: float,
        available_loads: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Suggest best backhaul load.
        
        Module 3: Dynamic Capacity Manager
        """
        system_prompt = """You are an AI freight optimizer.
Analyze available backhaul loads and recommend the best option.
Consider:
1. Route efficiency (minimize detour)
2. Revenue potential
3. Cargo compatibility
4. Time constraints

Respond in JSON format with keys: recommended_load_index, reasoning, estimated_profit, detour_km, confidence"""

        user_prompt = f"""Vehicle Status:
- Current Location: {current_location}
- Final Destination: {destination}
- Available Capacity: {vehicle_capacity} tons

Available Backhaul Loads:
{available_loads}

Which load should the driver pick up?"""

        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=user_prompt),
        ]
        
        response = await self.chat(messages, temperature=0.3)
        
        import json
        try:
            return json.loads(response.content)
        except:
            return {"raw_response": response.content}


# Singleton instance
_grok_client: Optional[GrokClient] = None


def get_grok_client() -> GrokClient:
    """Get or create Grok client singleton."""
    global _grok_client
    if _grok_client is None:
        _grok_client = GrokClient()
    return _grok_client
