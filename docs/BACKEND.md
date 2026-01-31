# Neuro-Logistics Backend Development Guide
## Python FastAPI + Agentic System Implementation

**Platform:** Google Antigravity  
**Framework:** Python FastAPI  
**Database:** PostgreSQL + PostGIS  
**ORM:** SQLAlchemy + GeoAlchemy2  
**Cache/Realtime:** Redis  
**Task Queue:** Celery  
**WebSocket:** FastAPI WebSockets  

---

## Table of Contents
1. [Architecture Overview](#1-architecture-overview)
2. [File Structure](#2-file-structure)
3. [Database Schema](#3-database-schema)
4. [API Specifications](#4-api-specifications)
5. [Agent System Design](#5-agent-system-design)
6. [Development Sequence](#6-development-sequence)
7. [File-by-File Implementation](#7-file-by-file-implementation)

---

## 1. Architecture Overview

### System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        C1[Driver App]
        C2[Fleet Dashboard]
        C3[External APIs]
    end
    
    subgraph "API Layer - FastAPI"
        AG[API Gateway<br/>Rate Limiting, CORS]
        AUTH[Auth Router]
        MISSION[Mission Router]
        VEHICLE[Vehicle Router]
        LOAD[Load Router]
        AGENT[Agent Router]
        WS[WebSocket Manager]
    end
    
    subgraph "Service Layer"
        AS[Auth Service]
        MS[Mission Service]
        VS[Vehicle Service]
        LS[Load Service]
        NS[Notification Service]
    end
    
    subgraph "Agent Core"
        AE[Agent Executor]
        DE[Decision Engine]
        PM[Policy Manager]
        TM[Trigger Manager]
    end
    
    subgraph "ML & Computation"
        FC[Fare Calculator]
        RO[Route Optimizer]
        LM[Load Matcher]
        BP[Backhaul Predictor]
        CP[Checkpoint Predictor]
    end
    
    subgraph "Data Layer"
        PG[(PostgreSQL + PostGIS)]
        RD[(Redis Cache)]
        CQ[Celery Queue]
    end
    
    subgraph "External Services"
        GM[Google Maps API]
        WA[Weather API]
        FP[Fuel Price API]
    end
    
    C1 --> AG
    C2 --> AG
    C3 --> AG
    
    AG --> AUTH
    AG --> MISSION
    AG --> VEHICLE
    AG --> LOAD
    AG --> AGENT
    AG --> WS
    
    AUTH --> AS
    MISSION --> MS
    VEHICLE --> VS
    LOAD --> LS
    
    MS --> AE
    VS --> AE
    LS --> AE
    
    AE --> DE
    DE --> PM
    DE --> TM
    
    DE --> FC
    DE --> RO
    DE --> LM
    DE --> BP
    DE --> CP
    
    AS --> PG
    MS --> PG
    VS --> PG
    LS --> PG
    
    AS --> RD
    MS --> RD
    AE --> RD
    
    AE --> CQ
    NS --> CQ
    
    RO --> GM
    AE --> WA
    FC --> FP
```

### Request Flow Architecture

```mermaid
sequenceDiagram
    participant C as Client
    participant API as FastAPI
    participant Auth as Auth Middleware
    participant S as Service Layer
    participant R as Repository
    participant DB as PostgreSQL
    participant Cache as Redis
    participant Agent as Agent Executor
    
    C->>API: HTTP Request
    API->>Auth: Validate JWT Token
    Auth-->>API: User Context
    API->>S: Call Service Method
    
    S->>Cache: Check Cache
    alt Cache Hit
        Cache-->>S: Cached Data
    else Cache Miss
        S->>R: Query Repository
        R->>DB: SQLAlchemy Query
        DB-->>R: Result Set
        R-->>S: Model Objects
        S->>Cache: Set Cache
    end
    
    opt Agent Decision Needed
        S->>Agent: Request Evaluation
        Agent->>Agent: Run Decision Loop
        Agent-->>S: Decision Result
    end
    
    S-->>API: Response Data
    API-->>C: JSON Response
```

### Agent Decision Loop

```mermaid
flowchart TB
    subgraph "Trigger Layer"
        T1[Scheduled Trigger<br/>Every 15 mins]
        T2[Event Trigger<br/>Traffic/Weather]
        T3[Location Trigger<br/>Geofence Entry]
        T4[Manual Trigger<br/>User Request]
    end
    
    subgraph "Agent Executor"
        AE1[Receive Trigger]
        AE2[Load Mission State]
        AE3[Gather Context]
        AE4[Run Policies]
        AE5[Evaluate Options]
        AE6[Select Best Action]
        AE7[Execute Action]
        AE8[Log Decision]
    end
    
    subgraph "Policies"
        P1[Reroute Policy]
        P2[Load Match Policy]
        P3[Backhaul Policy]
        P4[Refuel Policy]
        P5[Rest Stop Policy]
    end
    
    subgraph "Actions"
        A1[Update Route]
        A2[Send Notification]
        A3[Match Load]
        A4[Book Backhaul]
        A5[No Action]
    end
    
    T1 --> AE1
    T2 --> AE1
    T3 --> AE1
    T4 --> AE1
    
    AE1 --> AE2 --> AE3 --> AE4
    
    AE4 --> P1
    AE4 --> P2
    AE4 --> P3
    AE4 --> P4
    AE4 --> P5
    
    P1 --> AE5
    P2 --> AE5
    P3 --> AE5
    P4 --> AE5
    P5 --> AE5
    
    AE5 --> AE6 --> AE7 --> AE8
    
    AE7 --> A1
    AE7 --> A2
    AE7 --> A3
    AE7 --> A4
    AE7 --> A5
```

### Real-time WebSocket Flow

```mermaid
sequenceDiagram
    participant D as Driver App
    participant WS as WebSocket Manager
    participant RD as Redis Pub/Sub
    participant Agent as Agent Executor
    participant Fleet as Fleet Dashboard
    
    D->>WS: Connect (JWT Token)
    WS->>WS: Authenticate
    WS->>RD: Subscribe mission:{id}
    
    loop Every 30 seconds
        D->>WS: location_update
        WS->>RD: Publish vehicle:{id}:location
        WS->>Agent: Trigger location check
        RD-->>Fleet: Broadcast location
    end
    
    Agent->>Agent: Evaluate opportunity
    
    alt Opportunity Found
        Agent->>RD: Publish mission:{id}:opportunity
        RD-->>WS: Receive event
        WS-->>D: opportunity_available
        WS-->>Fleet: dashboard_update
        
        D->>WS: accept_opportunity
        WS->>Agent: Process acceptance
        Agent-->>WS: route_updated
        WS-->>D: new_route
    end
```

---

## 2. File Structure

### Complete Python Backend Structure

```
neuro-logistics-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                        # FastAPI application entry
│   ├── config.py                      # Configuration management
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                    # Dependency injection
│   │   ├── router.py                  # Main router aggregator
│   │   │
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                # Auth endpoints
│   │   │   ├── users.py               # User endpoints
│   │   │   ├── missions.py            # Mission endpoints
│   │   │   ├── vehicles.py            # Vehicle endpoints
│   │   │   ├── loads.py               # Load endpoints
│   │   │   ├── agent.py               # Agent endpoints
│   │   │   └── websocket.py           # WebSocket endpoints
│   │   │
│   │   └── schemas/
│   │       ├── __init__.py
│   │       ├── base.py                # Base schemas
│   │       ├── auth.py                # Auth schemas
│   │       ├── user.py                # User schemas
│   │       ├── mission.py             # Mission schemas
│   │       ├── vehicle.py             # Vehicle schemas
│   │       ├── load.py                # Load schemas
│   │       ├── agent.py               # Agent schemas
│   │       └── websocket.py           # WebSocket schemas
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py                # JWT, password hashing
│   │   ├── exceptions.py              # Custom exceptions
│   │   ├── middleware.py              # Custom middleware
│   │   └── events.py                  # Startup/shutdown events
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py                # Database connection
│   │   ├── base.py                    # Base model class
│   │   └── session.py                 # Session management
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                    # User model
│   │   ├── vehicle.py                 # Vehicle model
│   │   ├── mission.py                 # Mission model
│   │   ├── load.py                    # Load model
│   │   ├── waypoint.py                # Waypoint model
│   │   ├── decision.py                # Agent decision model
│   │   └── checkpoint.py              # Checkpoint model
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py                    # Base repository
│   │   ├── user.py                    # User repository
│   │   ├── vehicle.py                 # Vehicle repository
│   │   ├── mission.py                 # Mission repository
│   │   ├── load.py                    # Load repository
│   │   └── decision.py                # Decision repository
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth.py                    # Authentication service
│   │   ├── user.py                    # User service
│   │   ├── mission.py                 # Mission service
│   │   ├── vehicle.py                 # Vehicle service
│   │   ├── load.py                    # Load service
│   │   ├── notification.py            # Notification service
│   │   └── external/
│   │       ├── __init__.py
│   │       ├── maps.py                # Google Maps service
│   │       ├── weather.py             # Weather API service
│   │       └── fuel.py                # Fuel price service
│   │
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── executor.py                # Main agent executor
│   │   ├── state.py                   # Agent state management
│   │   ├── memory.py                  # Agent memory/context
│   │   ├── scheduler.py               # Agent task scheduler
│   │   │
│   │   ├── triggers/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # Base trigger class
│   │   │   ├── time_trigger.py        # Scheduled triggers
│   │   │   ├── location_trigger.py    # Geofence triggers
│   │   │   └── event_trigger.py       # External event triggers
│   │   │
│   │   ├── policies/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # Base policy class
│   │   │   ├── reroute.py             # Rerouting policy
│   │   │   ├── load_match.py          # Load matching policy
│   │   │   ├── backhaul.py            # Backhaul policy
│   │   │   ├── refuel.py              # Refuel stop policy
│   │   │   └── rest.py                # Rest stop policy
│   │   │
│   │   └── engines/
│   │       ├── __init__.py
│   │       ├── fare_calculator.py     # Dynamic fare calculation
│   │       ├── route_optimizer.py     # Route optimization
│   │       ├── load_matcher.py        # Load matching algorithm
│   │       ├── backhaul_predictor.py  # Backhaul prediction
│   │       ├── checkpoint_predictor.py# Checkpoint delay prediction
│   │       └── risk_assessor.py       # Risk assessment
│   │
│   ├── websocket/
│   │   ├── __init__.py
│   │   ├── manager.py                 # WebSocket connection manager
│   │   ├── handlers.py                # Event handlers
│   │   └── events.py                  # Event types
│   │
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── celery_app.py              # Celery configuration
│   │   ├── agent_tasks.py             # Agent background tasks
│   │   ├── notification_tasks.py      # Notification tasks
│   │   └── cleanup_tasks.py           # Data cleanup tasks
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py                  # Logging configuration
│       ├── geo.py                     # Geospatial utilities
│       ├── time_utils.py              # Time/date utilities
│       ├── validators.py              # Custom validators
│       └── helpers.py                 # Misc helpers
│
├── alembic/
│   ├── env.py                         # Alembic environment
│   ├── script.py.mako                 # Migration template
│   └── versions/                      # Migration files
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # Test fixtures
│   ├── test_auth.py
│   ├── test_missions.py
│   ├── test_vehicles.py
│   ├── test_loads.py
│   ├── test_agent.py
│   └── test_policies.py
│
├── scripts/
│   ├── seed_data.py                   # Seed database
│   ├── seed_checkpoints.py            # Indian checkpoints data
│   └── generate_demo.py               # Demo data generation
│
├── data/
│   ├── checkpoints.json               # Indian checkpoint data
│   ├── fuel_prices.json               # Sample fuel prices
│   └── sample_loads.json              # Sample loads
│
├── .env.example
├── requirements.txt
├── requirements-dev.txt
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 3. Database Schema

### Entity Relationship Diagram

```mermaid
erDiagram
    users ||--o{ vehicles : owns
    users ||--o{ missions : operates
    users ||--o{ missions : drives
    
    users {
        uuid id PK
        string type "driver|fleet_operator|admin"
        string name
        string phone UK
        string email
        string password_hash
        float rating
        boolean is_verified
        json preferences
        datetime created_at
        datetime updated_at
    }
    
    vehicles ||--o{ missions : assigned_to
    vehicles ||--o{ vehicle_locations : tracks
    
    vehicles {
        uuid id PK
        uuid owner_id FK
        string registration_number UK
        string vehicle_type
        string make
        string model
        int year
        json dimensions
        float max_capacity_tons
        float current_load_tons
        string status
        string fuel_type
        float fuel_level_percent
        float avg_fuel_efficiency
        date insurance_expiry
        date fitness_expiry
        date permit_expiry
        datetime created_at
    }
    
    vehicle_locations {
        uuid id PK
        uuid vehicle_id FK
        point location "PostGIS POINT"
        float speed_kmh
        float heading_degrees
        datetime recorded_at
    }
    
    missions ||--o{ mission_loads : contains
    missions ||--o{ waypoints : has
    missions ||--o{ agent_decisions : generates
    
    missions {
        uuid id PK
        string mission_number UK
        uuid operator_id FK
        uuid driver_id FK
        uuid vehicle_id FK
        string status
        point origin "PostGIS POINT"
        string origin_address
        point destination "PostGIS POINT"
        string destination_address
        point current_location "PostGIS POINT"
        json route_data
        datetime planned_start
        datetime actual_start
        datetime estimated_end
        datetime actual_end
        json quoted_fare
        json actual_fare
        string payment_status
        json risk_assessment
        datetime created_at
        datetime updated_at
    }
    
    loads ||--o{ mission_loads : matched_to
    
    loads {
        uuid id PK
        string shipper_id
        string shipper_name
        string shipper_phone
        float shipper_rating
        string cargo_type
        string description
        float weight_tons
        float volume_cbm
        point pickup_location "PostGIS POINT"
        string pickup_address
        string pickup_city
        datetime pickup_window_start
        datetime pickup_window_end
        point delivery_location "PostGIS POINT"
        string delivery_address
        string delivery_city
        datetime delivery_window_start
        datetime delivery_window_end
        float offered_rate
        string rate_type
        boolean negotiable
        string status
        uuid matched_mission_id FK
        datetime posted_at
        datetime expires_at
    }
    
    mission_loads {
        uuid id PK
        uuid mission_id FK
        uuid load_id FK
        int sequence
        string status
        datetime picked_at
        datetime delivered_at
    }
    
    waypoints {
        uuid id PK
        uuid mission_id FK
        int sequence
        point location "PostGIS POINT"
        string address
        string waypoint_type
        datetime eta
        datetime actual_arrival
        datetime actual_departure
        string notes
    }
    
    agent_decisions {
        uuid id PK
        uuid mission_id FK
        datetime timestamp
        string trigger_type
        string trigger_details
        json context_snapshot
        json options_evaluated
        string decision_type
        string decision_reason
        float confidence
        json action_details
        json outcome
        boolean was_overridden
        string overridden_by
        string override_reason
    }
    
    checkpoints {
        uuid id PK
        string name
        point location "PostGIS POINT"
        string state_from
        string state_to
        float avg_delay_minutes
        json delay_by_hour
        json delay_by_day
        boolean is_active
    }
```

---

## 4. API Specifications

### API Endpoint Summary

```mermaid
graph LR
    subgraph "Auth API /api/v1/auth"
        A1[POST /register]
        A2[POST /login]
        A3[POST /send-otp]
        A4[POST /verify-otp]
        A5[POST /refresh]
        A6[POST /logout]
    end
    
    subgraph "Users API /api/v1/users"
        U1[GET /me]
        U2[PATCH /me]
        U3[GET /:id]
    end
    
    subgraph "Missions API /api/v1/missions"
        M1[GET /]
        M2[POST /]
        M3[GET /:id]
        M4[PATCH /:id]
        M5[PATCH /:id/status]
        M6[GET /:id/route]
        M7[GET /:id/decisions]
    end
    
    subgraph "Vehicles API /api/v1/vehicles"
        V1[GET /]
        V2[POST /]
        V3[GET /:id]
        V4[PATCH /:id]
        V5[PATCH /:id/location]
        V6[GET /:id/history]
    end
    
    subgraph "Loads API /api/v1/loads"
        L1[GET /search]
        L2[GET /:id]
        L3[POST /:id/match]
        L4[GET /backhaul]
        L5[GET /opportunities]
    end
    
    subgraph "Agent API /api/v1/agent"
        AG1[GET /status/:missionId]
        AG2[GET /decisions/:missionId]
        AG3[GET /opportunities/:missionId]
        AG4[POST /trigger/:missionId]
        AG5[POST /override]
        AG6[GET /config/:missionId]
        AG7[PATCH /config/:missionId]
    end
```

### Request/Response Contracts

#### Create Mission
```
POST /api/v1/missions

Request:
{
    "origin": {
        "lat": 19.076,
        "lng": 72.877,
        "address": "Mumbai, Maharashtra"
    },
    "destination": {
        "lat": 18.520,
        "lng": 73.856,
        "address": "Pune, Maharashtra"
    },
    "vehicle_id": "uuid",
    "driver_id": "uuid",
    "planned_start": "2026-01-31T08:00:00Z",
    "load_details": {
        "weight_tons": 6,
        "cargo_type": "general",
        "description": "Electronics goods"
    },
    "constraints": {
        "max_detour_km": 30,
        "avoid_tolls": false
    }
}

Response:
{
    "success": true,
    "data": {
        "mission": {
            "id": "uuid",
            "mission_number": "NL-2026-0001",
            "status": "planned",
            ...
        },
        "route": {
            "polyline": "encoded_string",
            "distance_km": 150,
            "duration_minutes": 240,
            "waypoints": [...]
        },
        "fare": {
            "base": 8000,
            "distance_charge": 2250,
            "fuel_surcharge": 1500,
            "toll_charges": 350,
            "difficulty_premium": 400,
            "total": 12500,
            "currency": "INR"
        },
        "risk_assessment": {
            "overall_score": 0.35,
            "factors": [
                {
                    "type": "checkpoint_delay",
                    "probability": 0.6,
                    "impact_minutes": 45,
                    "location": "Maharashtra-Karnataka Border"
                }
            ],
            "eta_range": {
                "optimistic": "2026-01-31T12:00:00Z",
                "realistic": "2026-01-31T13:30:00Z",
                "pessimistic": "2026-01-31T15:00:00Z"
            }
        }
    }
}
```

---

## 5. Agent System Design

### Agent State Machine

```mermaid
stateDiagram-v2
    [*] --> IDLE: Agent Initialized
    
    IDLE --> MONITORING: Mission Started
    
    MONITORING --> TRIGGERED: Trigger Received
    
    TRIGGERED --> GATHERING_CONTEXT: Valid Trigger
    TRIGGERED --> MONITORING: Invalid/Duplicate
    
    GATHERING_CONTEXT --> EVALUATING: Context Ready
    
    EVALUATING --> DECIDING: Options Generated
    
    DECIDING --> EXECUTING: Decision Made
    DECIDING --> MONITORING: No Action Needed
    
    EXECUTING --> NOTIFYING: Action Executed
    
    NOTIFYING --> LOGGING: Notification Sent
    
    LOGGING --> MONITORING: Decision Logged
    
    MONITORING --> IDLE: Mission Completed
    
    MONITORING --> [*]: Mission Cancelled
```

### Policy Evaluation Flow

```mermaid
flowchart TB
    subgraph "Context"
        C1[Vehicle State]
        C2[Mission State]
        C3[External Data]
        C4[Available Loads]
    end
    
    subgraph "Policy Evaluation"
        PE[Policy Evaluator]
        
        subgraph "Policies"
            P1[Reroute Policy]
            P2[Load Match Policy]
            P3[Backhaul Policy]
            P4[Refuel Policy]
            P5[Rest Policy]
        end
        
        subgraph "Scores"
            S1[Reroute Score]
            S2[Load Match Score]
            S3[Backhaul Score]
            S4[Refuel Score]
            S5[Rest Score]
        end
    end
    
    subgraph "Decision"
        D1{Score > Threshold?}
        D2[Select Highest Score]
        D3[No Action]
        D4[Execute Best Action]
    end
    
    C1 --> PE
    C2 --> PE
    C3 --> PE
    C4 --> PE
    
    PE --> P1 --> S1
    PE --> P2 --> S2
    PE --> P3 --> S3
    PE --> P4 --> S4
    PE --> P5 --> S5
    
    S1 --> D1
    S2 --> D1
    S3 --> D1
    S4 --> D1
    S5 --> D1
    
    D1 -->|Yes| D2
    D1 -->|No| D3
    
    D2 --> D4
```

---

## 6. Development Sequence

### Phase-wise Development Plan

```mermaid
gantt
    title Backend Development Sequence (24 Hour Hackathon)
    dateFormat HH:mm
    axisFormat %H:%M
    
    section Phase 1: Foundation (0-4 hrs)
    Project Setup & Dependencies         :p1, 00:00, 30m
    Configuration & Environment          :p2, after p1, 30m
    Database Models                      :p3, after p2, 60m
    Database Connection & Migrations     :p4, after p3, 30m
    Base Repository Pattern              :p5, after p4, 30m
    
    section Phase 2: Core APIs (4-10 hrs)
    Auth Service & Routes                :p6, 04:00, 60m
    User Service & Routes                :p7, after p6, 45m
    Mission Service & Routes             :p8, after p7, 90m
    Vehicle Service & Routes             :p9, after p8, 60m
    Load Service & Routes                :p10, after p9, 60m
    
    section Phase 3: Agent System (10-18 hrs)
    Agent Executor Core                  :p11, 10:00, 90m
    Trigger System                       :p12, after p11, 60m
    Reroute Policy                       :p13, after p12, 60m
    Load Match Policy                    :p14, after p13, 60m
    Backhaul Policy                      :p15, after p14, 45m
    Fare Calculator Engine               :p16, 14:00, 60m
    Route Optimizer Engine               :p17, after p16, 60m
    
    section Phase 4: Real-time (18-22 hrs)
    WebSocket Manager                    :p18, 18:00, 60m
    WebSocket Handlers                   :p19, after p18, 45m
    Redis Pub/Sub Integration            :p20, after p19, 45m
    Celery Background Tasks              :p21, after p20, 45m
    
    section Phase 5: Polish (22-24 hrs)
    Integration Testing                  :p22, 22:00, 45m
    Seed Data & Demo Setup               :p23, after p22, 30m
    Final Fixes                          :p24, 23:15, 45m
```

---

## 7. File-by-File Implementation

Below are all files with their purpose, key requirements, and Antigravity prompts.

---

### FILE 1: Project Initialization

**File:** `requirements.txt`  
**Purpose:** Define all Python dependencies  
**Sequence:** 1 of 50

#### Understanding
This file lists all Python packages needed for the backend. We use FastAPI for the web framework, SQLAlchemy for ORM, and various other packages for specific functionality like geospatial operations, background tasks, and JWT authentication.

#### Antigravity Prompt
```
Create a requirements.txt file for a Python FastAPI backend with the following dependencies:

# Web Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
geoalchemy2==0.14.3
alembic==1.13.1

# Redis & Caching
redis==5.0.1
aioredis==2.0.1

# Background Tasks
celery==5.3.6
flower==2.0.1

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pydantic[email]==2.5.3
pydantic-settings==2.1.0

# HTTP Client
httpx==0.26.0
aiohttp==3.9.1

# Utilities
python-dateutil==2.8.2
pytz==2024.1
shapely==2.0.2
polyline==2.0.0

# Logging & Monitoring
loguru==0.7.2
sentry-sdk==1.39.1

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
httpx==0.26.0

# Development
black==24.1.1
isort==5.13.2
flake8==7.0.0
mypy==1.8.0

# WebSockets
websockets==12.0

# Geospatial
geopy==2.4.1
```

#### Verification Checklist
- [ ] FastAPI and uvicorn present for web server
- [ ] SQLAlchemy and psycopg2 for PostgreSQL
- [ ] GeoAlchemy2 for PostGIS support
- [ ] Redis and Celery for caching and background tasks
- [ ] Authentication packages (jose, passlib)
- [ ] Testing packages (pytest)
- [ ] All versions specified

#### Git Commit Command
```bash
git add requirements.txt
git commit -m "chore: initialize Python project with dependencies"
```

---

### FILE 2: Environment Configuration

**File:** `app/config.py`  
**Purpose:** Centralized configuration management using Pydantic Settings  
**Sequence:** 2 of 50

#### Understanding
This file manages all environment variables with type safety, validation, and default values. It uses Pydantic's Settings class for automatic environment variable loading.

#### Antigravity Prompt
```
Create app/config.py with Pydantic Settings for configuration management:

from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn, RedisDsn
from typing import Optional, List
from functools import lru_cache

class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Neuro-Logistics API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = Field(default="development", pattern="^(development|staging|production)$")
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # Database - PostgreSQL with PostGIS
    DATABASE_URL: PostgresDsn
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_ECHO: bool = False  # SQL query logging
    
    # Redis
    REDIS_URL: RedisDsn = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600  # 1 hour default cache TTL
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # JWT Authentication
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # External APIs
    GOOGLE_MAPS_API_KEY: str = ""
    WEATHER_API_KEY: str = ""
    FUEL_API_URL: str = "https://api.example.com/fuel"
    
    # Agent Configuration
    AGENT_CHECK_INTERVAL_MINUTES: int = 15
    AGENT_MIN_PROFIT_THRESHOLD: float = 500.0  # INR
    AGENT_MAX_DETOUR_KM: float = 30.0
    AGENT_MAX_DETOUR_MINUTES: int = 45
    
    # Geospatial
    DEFAULT_SRID: int = 4326  # WGS 84
    CORRIDOR_WIDTH_KM: float = 20.0  # Default load search corridor
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

# Convenience instance
settings = get_settings()
```

Also create .env.example with all variables documented:

```
# Application
APP_NAME=Neuro-Logistics API
DEBUG=true
ENVIRONMENT=development

# Server
HOST=0.0.0.0
PORT=8000

# Database (PostgreSQL + PostGIS)
DATABASE_URL=postgresql://postgres:password@localhost:5432/neuro_logistics

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-in-production

# External APIs
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
WEATHER_API_KEY=your-weather-api-key

# Agent
AGENT_CHECK_INTERVAL_MINUTES=15
AGENT_MIN_PROFIT_THRESHOLD=500
```

#### Verification Checklist
- [ ] All settings have proper types and defaults
- [ ] PostgresDsn and RedisDsn used for URL validation
- [ ] JWT settings for authentication
- [ ] Agent-specific configuration parameters
- [ ] CORS origins for frontend integration
- [ ] @lru_cache for singleton pattern
- [ ] .env.example created with documentation

#### Git Commit Command
```bash
git add app/config.py .env.example
git commit -m "feat: add configuration management with Pydantic Settings"
```

---

### FILE 3: Database Connection

**File:** `app/db/database.py`  
**Purpose:** SQLAlchemy engine and session setup with PostGIS support  
**Sequence:** 3 of 50

#### Understanding
Sets up the database connection with SQLAlchemy async support, connection pooling, and PostGIS extension for geospatial queries.

#### Antigravity Prompt
```
Create app/db/database.py with SQLAlchemy database setup:

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    str(settings.DATABASE_URL),
    poolclass=QueuePool,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,  # Verify connections before use
    echo=settings.DB_ECHO,  # Log SQL queries if enabled
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    
    Usage in FastAPI:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions outside of FastAPI request context.
    
    Usage:
        with get_db_context() as db:
            db.query(...)
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def init_db() -> None:
    """
    Initialize database - create PostGIS extension and tables.
    Called on application startup.
    """
    from app.db.base import Base
    from sqlalchemy import text
    
    with engine.connect() as conn:
        # Enable PostGIS extension
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        conn.commit()
        logger.info("PostGIS extension enabled")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

def check_db_connection() -> bool:
    """Health check for database connection."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

# Event listener for connection debugging
@event.listens_for(engine, "connect")
def on_connect(dbapi_conn, connection_record):
    logger.debug("New database connection established")

@event.listens_for(engine, "checkout")
def on_checkout(dbapi_conn, connection_record, connection_proxy):
    logger.debug("Connection checked out from pool")
```

#### Verification Checklist
- [ ] Engine created with connection pooling
- [ ] PostGIS extension initialization
- [ ] Dependency injection function get_db()
- [ ] Context manager for non-request usage
- [ ] Health check function
- [ ] Event listeners for debugging
- [ ] Proper error handling

#### Git Commit Command
```bash
git add app/db/database.py
git commit -m "feat: add database connection with PostGIS support"
```

---

### FILE 4: Base Model

**File:** `app/db/base.py`  
**Purpose:** SQLAlchemy declarative base with common model mixins  
**Sequence:** 4 of 50

#### Understanding
Defines the base class for all SQLAlchemy models with common fields (id, created_at, updated_at) and utility methods.

#### Antigravity Prompt
```
Create app/db/base.py with SQLAlchemy base model and mixins:

from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, declared_attr
from sqlalchemy.ext.declarative import DeclarativeMeta
import uuid
from datetime import datetime
from typing import Any

class CustomBase:
    """
    Custom base class for all models with common functionality.
    """
    
    # Generate __tablename__ automatically from class name
    @declared_attr
    def __tablename__(cls) -> str:
        """Convert CamelCase to snake_case for table name."""
        name = cls.__name__
        return ''.join(
            ['_' + c.lower() if c.isupper() else c for c in name]
        ).lstrip('_') + 's'
    
    # Common columns for all models
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def update(self, **kwargs) -> None:
        """Update model attributes from keyword arguments."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def __repr__(self) -> str:
        """String representation of model."""
        return f"<{self.__class__.__name__}(id={self.id})>"

# Create the declarative base
Base = declarative_base(cls=CustomBase)

class TimestampMixin:
    """Mixin for models that need timestamp tracking."""
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

class SoftDeleteMixin:
    """Mixin for models that support soft deletion."""
    
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
    
    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
    
    def soft_delete(self) -> None:
        self.deleted_at = datetime.utcnow()
    
    def restore(self) -> None:
        self.deleted_at = None
```

Also create app/db/__init__.py:

```python
from app.db.base import Base
from app.db.database import engine, SessionLocal, get_db, get_db_context, init_db

__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    "get_db_context",
    "init_db",
]
```

#### Verification Checklist
- [ ] UUID primary key with auto-generation
- [ ] Automatic table name from class name
- [ ] created_at and updated_at timestamps
- [ ] to_dict() method for serialization
- [ ] update() method for partial updates
- [ ] SoftDeleteMixin for soft deletion
- [ ] __init__.py exports all needed symbols

#### Git Commit Command
```bash
git add app/db/base.py app/db/__init__.py
git commit -m "feat: add SQLAlchemy base model with common mixins"
```

---

### FILE 5: User Model

**File:** `app/models/user.py`  
**Purpose:** User database model for drivers and fleet operators  
**Sequence:** 5 of 50

#### Understanding
Defines the User model with all fields needed for both drivers and fleet operators, including authentication fields, ratings, and preferences.

#### Antigravity Prompt
```
Create app/models/user.py with the User SQLAlchemy model:

from sqlalchemy import Column, String, Float, Boolean, Enum, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
import enum
from typing import Optional, List

from app.db.base import Base

class UserType(str, enum.Enum):
    """User type enumeration."""
    DRIVER = "driver"
    FLEET_OPERATOR = "fleet_operator"
    ADMIN = "admin"

class User(Base):
    """
    User model representing drivers, fleet operators, and admins.
    
    Attributes:
        type: Type of user (driver, fleet_operator, admin)
        name: Full name of the user
        phone: Phone number (unique, used for OTP login)
        email: Email address (optional)
        password_hash: Hashed password for authentication
        rating: Average rating (1-5 scale)
        is_verified: Whether phone/identity is verified
        is_active: Whether account is active
        preferences: JSON object with user preferences
        
    Driver-specific fields:
        license_number: Driving license number
        license_expiry: License expiry date
        experience_years: Years of driving experience
        total_trips: Total completed trips
        total_earnings: Total earnings in INR
        
    Fleet operator-specific fields:
        company_name: Company/business name
        gst_number: GST registration number
    """
    
    # Core fields
    type = Column(
        Enum(UserType),
        nullable=False,
        index=True,
    )
    
    name = Column(String(100), nullable=False)
    
    phone = Column(
        String(15),
        unique=True,
        nullable=False,
        index=True,
    )
    
    email = Column(String(255), unique=True, nullable=True)
    
    password_hash = Column(String(255), nullable=True)
    
    # Status
    rating = Column(Float, default=5.0)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Preferences (JSON)
    preferences = Column(
        JSONB,
        default=lambda: {
            "language": "en",
            "notifications": {
                "push": True,
                "sms": True,
                "email": False,
            },
            "default_vehicle_id": None,
        },
    )
    
    # Driver-specific fields
    license_number = Column(String(50), nullable=True)
    license_expiry = Column(String(10), nullable=True)  # YYYY-MM-DD
    experience_years = Column(Float, nullable=True)
    total_trips = Column(Float, default=0)
    total_earnings = Column(Float, default=0.0)
    
    # Fleet operator-specific fields
    company_name = Column(String(200), nullable=True)
    gst_number = Column(String(20), nullable=True)
    
    # Avatar/profile image
    avatar_url = Column(Text, nullable=True)
    
    # Relationships
    owned_vehicles = relationship(
        "Vehicle",
        back_populates="owner",
        foreign_keys="Vehicle.owner_id",
    )
    
    operated_missions = relationship(
        "Mission",
        back_populates="operator",
        foreign_keys="Mission.operator_id",
    )
    
    driven_missions = relationship(
        "Mission",
        back_populates="driver",
        foreign_keys="Mission.driver_id",
    )
    
    # Properties
    @property
    def is_driver(self) -> bool:
        return self.type == UserType.DRIVER
    
    @property
    def is_fleet_operator(self) -> bool:
        return self.type == UserType.FLEET_OPERATOR
    
    @property
    def is_admin(self) -> bool:
        return self.type == UserType.ADMIN
    
    @property
    def display_name(self) -> str:
        if self.company_name:
            return f"{self.name} ({self.company_name})"
        return self.name
    
    def update_rating(self, new_rating: float, total_ratings: int) -> None:
        """Update user rating using running average."""
        self.rating = (
            (self.rating * (total_ratings - 1) + new_rating) / total_ratings
        )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, name={self.name}, type={self.type})>"
```

Also create app/models/__init__.py:

```python
from app.models.user import User, UserType

__all__ = [
    "User",
    "UserType",
]
```

#### Verification Checklist
- [ ] UserType enum for driver/fleet_operator/admin
- [ ] Phone number is unique and indexed
- [ ] JSONB preferences field with defaults
- [ ] Driver-specific fields (license, experience)
- [ ] Fleet operator fields (company, GST)
- [ ] Relationships defined (vehicles, missions)
- [ ] Helper properties (is_driver, is_fleet_operator)
- [ ] Rating update method

#### Git Commit Command
```bash
git add app/models/user.py app/models/__init__.py
git commit -m "feat: add User model with driver and fleet operator support"
```

---

### FILE 6: Vehicle Model

**File:** `app/models/vehicle.py`  
**Purpose:** Vehicle database model with geospatial support  
**Sequence:** 6 of 50

#### Understanding
Defines the Vehicle model with Indian-specific vehicle types, capacity tracking for LTL (Less Than Truckload) support, and PostGIS location tracking.

#### Antigravity Prompt
```
Create app/models/vehicle.py with the Vehicle SQLAlchemy model:

from sqlalchemy import Column, String, Float, Integer, Enum, Date, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
import enum
from typing import Optional

from app.db.base import Base

class VehicleType(str, enum.Enum):
    """Indian logistics vehicle types."""
    MINI_TRUCK = "mini_truck"        # Tata Ace, Mahindra Bolero Pickup
    LCV = "lcv"                       # Light Commercial Vehicle (< 7.5 ton)
    ICV = "icv"                       # Intermediate Commercial Vehicle (7.5-12 ton)
    MCV = "mcv"                       # Medium Commercial Vehicle (12-16 ton)
    HCV = "hcv"                       # Heavy Commercial Vehicle (16-25 ton)
    MAV = "mav"                       # Multi-Axle Vehicle (> 25 ton)
    TRAILER = "trailer"               # Trailer trucks
    CONTAINER = "container"           # Container trucks (20ft/40ft)

class VehicleStatus(str, enum.Enum):
    """Vehicle operational status."""
    AVAILABLE = "available"
    ON_MISSION = "on_mission"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"

class FuelType(str, enum.Enum):
    """Fuel type enumeration."""
    DIESEL = "diesel"
    PETROL = "petrol"
    CNG = "cng"
    ELECTRIC = "electric"

class Vehicle(Base):
    """
    Vehicle model for trucks in the logistics system.
    
    Supports:
    - Indian vehicle categorization (LCV, HCV, etc.)
    - Real-time location tracking with PostGIS
    - Capacity management for LTL operations
    - Compliance tracking (insurance, fitness, permits)
    """
    
    # Owner relationship
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    
    # Identification
    registration_number = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )
    
    vehicle_type = Column(
        Enum(VehicleType),
        nullable=False,
        index=True,
    )
    
    make = Column(String(50), nullable=False)  # Tata, Ashok Leyland, etc.
    model = Column(String(50), nullable=False)  # Prima, Captain, etc.
    year = Column(Integer, nullable=False)
    
    # Dimensions (stored as JSON for flexibility)
    dimensions = Column(
        JSONB,
        default=lambda: {
            "length_m": 0,
            "width_m": 0,
            "height_m": 0,
        },
    )
    
    # Capacity
    max_capacity_tons = Column(Float, nullable=False)
    current_load_tons = Column(Float, default=0.0)
    volume_capacity_cbm = Column(Float, nullable=True)  # Cubic meters
    current_volume_cbm = Column(Float, default=0.0)
    
    # Status
    status = Column(
        Enum(VehicleStatus),
        default=VehicleStatus.AVAILABLE,
        nullable=False,
        index=True,
    )
    
    # Current location (PostGIS Geography for accurate distance calculations)
    current_location = Column(
        Geography(geometry_type="POINT", srid=4326),
        nullable=True,
    )
    last_location_update = Column(String(30), nullable=True)  # ISO timestamp
    
    # Fuel
    fuel_type = Column(
        Enum(FuelType),
        default=FuelType.DIESEL,
        nullable=False,
    )
    fuel_level_percent = Column(Float, default=100.0)
    tank_capacity_liters = Column(Float, nullable=True)
    avg_fuel_efficiency = Column(Float, nullable=True)  # km per liter
    
    # Compliance (Indian regulations)
    insurance_expiry = Column(Date, nullable=True)
    fitness_expiry = Column(Date, nullable=True)
    permit_type = Column(String(50), nullable=True)  # National, State, etc.
    permit_states = Column(JSONB, default=list)  # List of permitted states
    permit_expiry = Column(Date, nullable=True)
    puc_expiry = Column(Date, nullable=True)  # Pollution Under Control
    
    # Assigned driver (optional)
    assigned_driver_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    
    # Statistics
    total_trips = Column(Integer, default=0)
    total_km = Column(Float, default=0.0)
    
    # Active mission
    current_mission_id = Column(
        UUID(as_uuid=True),
        nullable=True,
    )
    
    # Images
    images = Column(JSONB, default=list)  # List of image URLs
    
    # Relationships
    owner = relationship(
        "User",
        back_populates="owned_vehicles",
        foreign_keys=[owner_id],
    )
    
    missions = relationship(
        "Mission",
        back_populates="vehicle",
        foreign_keys="Mission.vehicle_id",
    )
    
    location_history = relationship(
        "VehicleLocation",
        back_populates="vehicle",
        order_by="desc(VehicleLocation.recorded_at)",
    )
    
    # Properties
    @property
    def available_capacity_tons(self) -> float:
        """Calculate available weight capacity."""
        return max(0, self.max_capacity_tons - self.current_load_tons)
    
    @property
    def capacity_utilization_percent(self) -> float:
        """Calculate capacity utilization percentage."""
        if self.max_capacity_tons == 0:
            return 0
        return (self.current_load_tons / self.max_capacity_tons) * 100
    
    @property
    def is_available(self) -> bool:
        """Check if vehicle is available for new missions."""
        return self.status == VehicleStatus.AVAILABLE
    
    @property
    def has_space(self) -> bool:
        """Check if vehicle has space for additional load."""
        return self.available_capacity_tons > 0.5  # At least 0.5 ton available
    
    def add_load(self, weight_tons: float) -> bool:
        """Add load to vehicle if capacity available."""
        if weight_tons <= self.available_capacity_tons:
            self.current_load_tons += weight_tons
            return True
        return False
    
    def remove_load(self, weight_tons: float) -> None:
        """Remove load from vehicle."""
        self.current_load_tons = max(0, self.current_load_tons - weight_tons)
    
    def __repr__(self) -> str:
        return f"<Vehicle(id={self.id}, reg={self.registration_number}, type={self.vehicle_type})>"


class VehicleLocation(Base):
    """
    Vehicle location history for tracking and analytics.
    Stores periodic location updates with speed and heading.
    """
    
    __tablename__ = "vehicle_locations"
    
    vehicle_id = Column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id"),
        nullable=False,
        index=True,
    )
    
    location = Column(
        Geography(geometry_type="POINT", srid=4326),
        nullable=False,
    )
    
    speed_kmh = Column(Float, nullable=True)
    heading_degrees = Column(Float, nullable=True)  # 0-360
    
    recorded_at = Column(String(30), nullable=False)  # ISO timestamp
    
    # Network status when recorded
    network_status = Column(String(20), default="online")
    
    # Relationship
    vehicle = relationship(
        "Vehicle",
        back_populates="location_history",
    )
```

Update app/models/__init__.py:

```python
from app.models.user import User, UserType
from app.models.vehicle import Vehicle, VehicleLocation, VehicleType, VehicleStatus, FuelType

__all__ = [
    "User",
    "UserType",
    "Vehicle",
    "VehicleLocation",
    "VehicleType",
    "VehicleStatus",
    "FuelType",
]
```

#### Verification Checklist
- [ ] VehicleType enum covers Indian vehicle categories
- [ ] PostGIS Geography column for current_location
- [ ] Capacity tracking for LTL (current_load_tons, available_capacity)
- [ ] Indian compliance fields (insurance, fitness, PUC, permits)
- [ ] FuelType enum with CNG and electric support
- [ ] VehicleLocation model for tracking history
- [ ] Helper properties and methods (has_space, add_load)
- [ ] Proper relationships to User and Mission

#### Git Commit Command
```bash
git add app/models/vehicle.py app/models/__init__.py
git commit -m "feat: add Vehicle model with Indian logistics support and PostGIS"
```

---

### FILE 7: Mission Model

**File:** `app/models/mission.py`  
**Purpose:** Core Mission/Trip model - the central entity of the system  
**Sequence:** 7 of 50

#### Understanding
The Mission is the central entity representing a trip from origin to destination. It tracks status, route, fare, risk assessment, and connects to vehicles, drivers, loads, and agent decisions.

#### Antigravity Prompt
```
Create app/models/mission.py with the Mission SQLAlchemy model:

from sqlalchemy import Column, String, Float, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
import enum
from typing import Optional, List
from datetime import datetime

from app.db.base import Base

class MissionStatus(str, enum.Enum):
    """Mission lifecycle status."""
    DRAFT = "draft"                 # Initial creation
    PLANNED = "planned"             # Route and fare calculated
    ASSIGNED = "assigned"           # Vehicle and driver assigned
    EN_ROUTE_PICKUP = "en_route_pickup"  # Going to pickup
    AT_PICKUP = "at_pickup"         # Arrived at pickup
    LOADING = "loading"             # Loading cargo
    IN_TRANSIT = "in_transit"       # Moving to destination
    AT_DELIVERY = "at_delivery"     # Arrived at destination
    UNLOADING = "unloading"         # Unloading cargo
    COMPLETED = "completed"         # Successfully completed
    CANCELLED = "cancelled"         # Cancelled

class PaymentStatus(str, enum.Enum):
    """Payment status for mission."""
    PENDING = "pending"
    PARTIAL = "partial"
    COMPLETED = "completed"
    REFUNDED = "refunded"

class Mission(Base):
    """
    Mission model - represents a complete trip from origin to destination.
    
    The Mission is the central entity that connects:
    - Operator (fleet owner who creates the mission)
    - Driver (person driving the vehicle)
    - Vehicle (truck assigned to the mission)
    - Loads (cargo being transported)
    - Waypoints (stops along the route)
    - Agent Decisions (AI decisions made during the trip)
    """
    
    # Human-readable mission number
    mission_number = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )
    
    # Participants
    operator_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    
    driver_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    
    vehicle