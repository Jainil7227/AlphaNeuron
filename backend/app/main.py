"""
Neuro-Logistics Backend API

A clean, AI-powered logistics system with 3 core modules:
1. Context-Aware Mission Planner - Dynamic routing and pricing
2. Rolling Decision Engine - Real-time trip adaptation
3. Dynamic Capacity Manager - LTL pooling and backhauling

No SQL database or Google Maps dependencies.
Uses in-memory storage and Gemini AI.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.config import settings


# Create FastAPI app
app = FastAPI(
    title="Neuro-Logistics API",
    description="""
    AI-powered logistics system that transforms road freight from a static process
    into a fluid, intelligent operation.
    
    ## Core Modules
    
    ### Module 1: Context-Aware Mission Planner
    Solves static pricing and route rigidity at trip start.
    - Infrastructure-aware routing (checkpost delays, no-entry timings)
    - Dynamic fare engine based on effort, not just distance
    - ETA range with optimistic/expected/pessimistic estimates
    
    ### Module 2: Rolling Decision Engine
    Solves variable time and inability to adapt during trip.
    - Continuous monitoring loop (Observe → Reason → Decide)
    - Opportunity vs. Cost calculator
    - Autonomous rerouting recommendations
    
    ### Module 3: Dynamic Capacity Manager
    Solves empty returns and partial capacity utilization.
    - En-route LTL pooling (fill unused capacity)
    - Predictive backhauling (pre-book return loads)
    - Fleet-wide capacity optimization
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routes
app.include_router(api_router, prefix="/api")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Neuro-Logistics API",
        "version": "2.0.0",
        "status": "running",
        "modules": [
            "Mission Planner",
            "Decision Engine",
            "Capacity Manager",
        ],
        "docs": "/docs",
        "health": "/api/health",
    }


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    print("🚀 Neuro-Logistics API starting...")
    print(f"📍 Gemini Model: {settings.GEMINI_MODEL}")
    if settings.GEMINI_API_KEY:
        print("✅ Gemini API key configured")
    else:
        print("⚠️  Gemini API key not configured - AI features limited")
    print("✅ All modules initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    print("👋 Neuro-Logistics API shutting down...")
