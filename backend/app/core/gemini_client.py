"""
Gemini AI Client for Neuro-Logistics

Handles all AI-powered decision making for the 3 core modules:
1. Mission Planner - Route analysis and fare calculation
2. Decision Engine - Real-time opportunity evaluation
3. Capacity Manager - Load matching and backhaul suggestions
"""

import httpx
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from app.config import settings


class Message(BaseModel):
    """Chat message."""
    role: str  # "system", "user", "model"
    content: str


class GeminiResponse(BaseModel):
    """Gemini API response."""
    content: str
    model: str
    usage: Dict[str, Any] = {}


class GeminiClient:
    """
    Gemini AI client for intelligent logistics decisions.
    """
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL
        self.temperature = settings.GEMINI_TEMPERATURE
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        
        if not self.api_key:
            print("⚠️  GEMINI_API_KEY not configured - AI features will be limited")
    
    async def chat(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
    ) -> GeminiResponse:
        """Send chat completion request to Gemini."""
        if not self.api_key:
            return GeminiResponse(
                content='{"error": "API key not configured"}',
                model=self.model,
                usage={}
            )
        
        # Separate system prompt from history
        system_instruction = None
        contents = []
        
        for m in messages:
            if m.role == "system":
                system_instruction = {"parts": [{"text": m.content}]}
            elif m.role == "user":
                contents.append({"role": "user", "parts": [{"text": m.content}]})
            elif m.role in ["assistant", "model"]:
                contents.append({"role": "model", "parts": [{"text": m.content}]})
                
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature or self.temperature,
            }
        }
    
        if system_instruction:
            payload["systemInstruction"] = system_instruction
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/{self.model}:generateContent?key={self.api_key}",
                    headers={"Content-Type": "application/json"},
                    json=payload,
                    timeout=60.0,
                )
                
                if response.status_code != 200:
                    error_msg = response.text
                    print(f"Gemini API Error: {error_msg}")
                    return GeminiResponse(
                        content=f'{{"error": "API error: {response.status_code}"}}',
                        model=self.model,
                        usage={}
                    )

                data = response.json()
                
            except Exception as e:
                print(f"Gemini request failed: {e}")
                return GeminiResponse(
                    content=f'{{"error": "Request failed: {str(e)}"}}',
                    model=self.model,
                    usage={}
                )
            
        # Extract content
        try:
            content = data["candidates"][0]["content"]["parts"][0]["text"]
            usage = data.get("usageMetadata", {})
        except (KeyError, IndexError) as e:
            content = '{"error": "Failed to parse response"}'
            usage = {}
            print(f"Error parsing Gemini response: {e}")
        
        return GeminiResponse(
            content=content,
            model=self.model,
            usage=usage,
        )
    
    def _parse_json(self, content: str) -> Dict[str, Any]:
        """Parse JSON from AI response, handling markdown code blocks."""
        import json
        
        cleaned_content = content.strip()
        
        # Remove markdown code blocks if present
        if cleaned_content.startswith("```"):
            lines = cleaned_content.split("\n")
            if len(lines) >= 2:
                cleaned_content = "\n".join(lines[1:-1])
        
        try:
            return json.loads(cleaned_content)
        except:
            # Try to find JSON substring
            try:
                start = content.find("{")
                end = content.rfind("}") + 1
                if start != -1 and end != 0:
                    return json.loads(content[start:end])
            except:
                pass
            return {"raw_response": content}
    
    # ==========================================
    # MODULE 1: MISSION PLANNER
    # ==========================================
    
    async def analyze_route(
        self,
        origin: str,
        destination: str,
        cargo_type: str,
        weight_tons: float,
    ) -> Dict[str, Any]:
        """
        Analyze a route and provide AI-powered insights.
        
        Returns route recommendations, risk factors, and realistic timing.
        """
        system_prompt = """You are an AI logistics expert specializing in Indian road freight.
Analyze the route and provide practical insights for truck transport.

Always respond in valid JSON format with these keys:
{
    "route_summary": "Brief description of the best route",
    "highways": ["List of major highways to take"],
    "estimated_hours": number (realistic driving time),
    "risk_factors": ["List of potential issues"],
    "checkpoints": ["State borders or major checkpoints"],
    "best_departure_time": "Recommended departure time",
    "fuel_stops": number (recommended fuel stops),
    "tips": ["Practical tips for this route"]
}"""

        user_prompt = f"""Analyze this freight route:
- Origin: {origin}
- Destination: {destination}
- Cargo: {cargo_type}
- Weight: {weight_tons} tons

Provide realistic routing for a heavy commercial vehicle in India."""

        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=user_prompt),
        ]
        
        response = await self.chat(messages, temperature=0.3)
        return self._parse_json(response.content)
    
    async def calculate_dynamic_fare(
        self,
        origin: str,
        destination: str,
        distance_km: float,
        cargo_type: str,
        weight_tons: float,
        risk_level: str = "medium",
    ) -> Dict[str, Any]:
        """
        Calculate a dynamic "fair fare" based on route difficulty.
        
        Unlike static per-km pricing, this accounts for real-world effort.
        """
        system_prompt = """You are a freight pricing expert for Indian logistics.
Calculate a fair, dynamic fare that accounts for real-world effort, not just distance.

Consider these factors:
- Fuel costs (current diesel ~₹90/liter)
- Toll costs on Indian highways
- Driver wages and rest requirements
- Route difficulty and risk factors
- Cargo type handling requirements
- Weight-based wear on vehicle

Respond in valid JSON:
{
    "base_fare": number (₹),
    "fuel_cost": number (₹),
    "toll_estimate": number (₹),
    "driver_allowance": number (₹),
    "risk_premium": number (₹),
    "handling_fee": number (₹),
    "total_fare": number (₹),
    "per_km_rate": number (₹),
    "effort_multiplier": number (1.0-2.0),
    "fare_justification": "Brief explanation"
}"""

        user_prompt = f"""Calculate fare for this trip:
- Route: {origin} to {destination}
- Distance: {distance_km} km
- Cargo: {cargo_type}
- Weight: {weight_tons} tons
- Risk Level: {risk_level}

Provide a fair fare that compensates for actual effort."""

        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=user_prompt),
        ]
        
        response = await self.chat(messages, temperature=0.2)
        return self._parse_json(response.content)
    
    # ==========================================
    # MODULE 2: DECISION ENGINE
    # ==========================================
    
    async def evaluate_situation(
        self,
        current_location: str,
        destination: str,
        progress_percent: float,
        current_conditions: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Evaluate the current situation and recommend actions.
        
        This is the "Observe → Reason → Decide" loop.
        """
        system_prompt = """You are an AI logistics supervisor running in a truck's dashboard.
Your job is to continuously monitor the trip and suggest improvements.

Analyze the current situation and provide actionable recommendations.

Respond in valid JSON:
{
    "situation_assessment": "Brief summary of current state",
    "observations": ["Key things noticed"],
    "risks": ["Potential problems ahead"],
    "opportunities": ["Ways to improve the trip"],
    "recommended_action": "CONTINUE | REROUTE | STOP | ALERT",
    "action_details": "Specific recommendation",
    "confidence": number (0-100),
    "updated_eta_hours": number or null
}"""

        conditions_str = "\n".join([f"- {k}: {v}" for k, v in current_conditions.items()])
        
        user_prompt = f"""Current Trip Status:
- Location: {current_location}
- Destination: {destination}
- Progress: {progress_percent}% complete

Current Conditions:
{conditions_str}

What should the driver do?"""

        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=user_prompt),
        ]
        
        response = await self.chat(messages, temperature=0.3)
        return self._parse_json(response.content)
    
    async def evaluate_opportunity(
        self,
        current_mission: Dict[str, Any],
        opportunity: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Evaluate if an opportunity (new load, reroute, etc.) is worth pursuing.
        
        Uses "Opportunity vs. Cost" calculation.
        """
        system_prompt = """You are an AI decision engine for freight logistics.
A new opportunity has appeared. Evaluate if it's worth pursuing.

Consider:
- Extra time required
- Additional fuel costs
- Revenue from the opportunity
- Impact on current delivery
- Driver fatigue

Respond in valid JSON:
{
    "recommendation": "ACCEPT | REJECT | CONSIDER",
    "net_benefit_inr": number (can be negative),
    "time_impact_hours": number,
    "fuel_cost_extra": number (₹),
    "revenue_gain": number (₹),
    "risk_assessment": "low | medium | high",
    "reasoning": "Brief explanation",
    "confidence": number (0-100)
}"""

        user_prompt = f"""Current Mission:
{current_mission}

New Opportunity:
{opportunity}

Should the driver take this opportunity?"""

        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=user_prompt),
        ]
        
        response = await self.chat(messages, temperature=0.2)
        return self._parse_json(response.content)
    
    # ==========================================
    # MODULE 3: CAPACITY MANAGER
    # ==========================================
    
    async def find_ltl_matches(
        self,
        current_route: str,
        available_capacity_tons: float,
        available_loads: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Find LTL (Less Than Truckload) matches to fill unused capacity.
        
        This is the "En-Route Pooling" feature.
        """
        system_prompt = """You are an AI capacity optimizer for freight.
The truck has unused space. Find the best loads to add.

Consider:
- Load fits available capacity
- Pickup/delivery aligns with current route
- Revenue is worth the extra stops
- Cargo compatibility

Respond in valid JSON:
{
    "recommended_loads": [
        {
            "load_id": "string",
            "reason": "why this is a good match",
            "estimated_extra_revenue": number (₹),
            "extra_time_hours": number,
            "priority": "high | medium | low"
        }
    ],
    "total_potential_revenue": number (₹),
    "capacity_utilization_after": number (percent),
    "recommendation_summary": "Brief advice"
}"""

        loads_str = "\n".join([str(load) for load in available_loads])
        
        user_prompt = f"""Current Route: {current_route}
Available Capacity: {available_capacity_tons} tons

Available Loads:
{loads_str}

Which loads should be pooled?"""

        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=user_prompt),
        ]
        
        response = await self.chat(messages, temperature=0.3)
        return self._parse_json(response.content)
    
    async def find_backhaul(
        self,
        current_destination: str,
        home_base: str,
        truck_capacity_tons: float,
        available_loads: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Find backhaul loads to avoid empty return trips.
        
        This is the "Predictive Backhauling" feature.
        """
        system_prompt = """You are an AI backhaul optimizer.
The truck is approaching its destination. Find return loads to avoid "dead miles."

Dead miles = driving empty = wasted money.

Respond in valid JSON:
{
    "recommended_backhaul": {
        "load_id": "string or null",
        "pickup_city": "string",
        "delivery_city": "string",  
        "cargo_type": "string",
        "weight_tons": number,
        "offered_rate": number (₹),
        "pickup_window": "string",
        "match_score": number (0-100)
    },
    "alternative_options": [
        { similar structure }
    ],
    "empty_return_cost": number (₹ that would be lost),
    "savings_with_backhaul": number (₹),
    "recommendation": "Brief advice"
}"""

        loads_str = "\n".join([str(load) for load in available_loads])
        
        user_prompt = f"""Current Destination: {current_destination}
Home Base: {home_base}
Truck Capacity: {truck_capacity_tons} tons

Available Return Loads:
{loads_str}

Find the best backhaul option."""

        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=user_prompt),
        ]
        
        response = await self.chat(messages, temperature=0.3)
        return self._parse_json(response.content)


# Singleton instance
_gemini_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """Get or create Gemini client singleton."""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
