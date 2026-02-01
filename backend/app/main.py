from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import api_router
from app.db import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    
    Startup:
    - Create database tables if they don't exist
    
    Shutdown:
    - Cleanup resources
    """
    # Startup
    print("🚀 Starting Neuro-Logistics API...")
    
    # Try to create tables (may fail if DB not available)
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables ready")
    except Exception as e:
        print(f"⚠️ Database not available: {e}")
        print("📝 Running in DEMO mode - some features may be limited")
    
    yield
    
    # Shutdown
    print("👋 Shutting down Neuro-Logistics API...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    ## Neuro-Logistics API
    
    AI-driven agentic system for road freight optimization.
    
    ### Three Core Modules:
    
    1. **Context-Aware Mission Planner** - Infrastructure-aware routing with dynamic fare calculation
    2. **Rolling Decision Engine** - Continuous monitoring with opportunity detection
    3. **Dynamic Capacity Manager** - LTL pooling and predictive backhauling
    
    ### Authentication
    
    Use `/api/v1/auth/login` to get JWT tokens.
    Include `Authorization: Bearer <token>` header in requests.
    """,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS configuration - support both specific origins and Netlify subdomains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=r"https://.*\.netlify\.app",  # Allow all Netlify subdomains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint for load balancers and monitoring.
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
    }


# Root endpoint
@app.get("/", tags=["Root"])
def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Welcome to Neuro-Logistics API",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "api": settings.API_V1_PREFIX,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
