# Product Requirements Document (PRD)
## Neuro-Logistics: Agentic Road Freight Optimization System

**Version:** 1.0  
**Date:** January 31, 2026  
**Hackathon Submission**

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Solution Overview](#3-solution-overview)
4. [System Architecture](#4-system-architecture)
5. [Module Specifications](#5-module-specifications)
6. [Data Models](#6-data-models)
7. [User Flows](#7-user-flows)
8. [API Specifications](#8-api-specifications)
9. [Tech Stack](#9-tech-stack)
10. [File Structure](#10-file-structure)
11. [Development Phases](#11-development-phases)
12. [Success Metrics](#12-success-metrics)

---

## 1. Executive Summary

**Product Name:** Neuro-Logistics  
**Tagline:** "From Static Routes to Adaptive Journeys"

Neuro-Logistics is an AI-driven logistics supervisor that transforms road freight from isolated, static trips into a continuous, adaptive operation. The system acts as an intelligent Co-Pilot that continuously **Observes**, **Reasons**, and **Acts** throughout the entire journey lifecycle.

### Key Differentiators
- **Agentic Architecture:** Autonomous decision-making without constant human intervention
- **India-Context Aware:** Built for checkposts, variable road conditions, and connectivity gaps
- **Real-time Adaptability:** Continuous re-optimization while vehicles are in motion
- **Multi-stakeholder Support:** Serves both individual drivers and fleet operators

---

## 2. Problem Statement

### The Three Pillars of Inefficiency

```mermaid
graph TD
    subgraph "Pillar 1: Static Plan Trap"
        A1[Price Locked Before Trip] --> A2[No Dynamic Fare Updates]
        A1 --> A3[Route Rigidity]
    end
    
    subgraph "Pillar 2: Dead Mile Crisis"
        B1[Empty Return Journeys] --> B2[40% Capacity Waste]
        B1 --> B3[No Backhaul Planning]
    end
    
    subgraph "Pillar 3: Indian Context Friction"
        C1[Checkpoint Delays] --> C2[Unrealistic ETAs]
        C1 --> C3[Connectivity Issues]
    end
    
    A2 --> D[Revenue Loss]
    A3 --> D
    B2 --> D
    B3 --> D
    C2 --> E[Operational Chaos]
    C3 --> E
    
    D --> F[Industry Inefficiency]
    E --> F
```

### Quantified Impact
| Problem | Current State | Target State |
|---------|--------------|--------------|
| Empty Return Trips | 35-40% of trips | <15% of trips |
| Capacity Utilization | 55-60% average | >80% average |
| Route Deviation Response | Manual, 30+ mins | Automated, <2 mins |
| Fare Accuracy | ±25% variance | ±8% variance |

---

## 3. Solution Overview

### The Neuro-Logistics Agentic System

```mermaid
graph TB
    subgraph "User Layer"
        D[Driver App]
        F[Fleet Dashboard]
    end
    
    subgraph "Agent Core"
        subgraph "Module 1: Context-Aware Mission Planner"
            M1A[Infrastructure Analyzer]
            M1B[Dynamic Fare Engine]
            M1C[Risk Assessor]
        end
        
        subgraph "Module 2: Rolling Decision Engine"
            M2A[Continuous Monitor]
            M2B[Opportunity Calculator]
            M2C[Auto Re-router]
        end
        
        subgraph "Module 3: Dynamic Capacity Manager"
            M3A[LTL Optimizer]
            M3B[Backhaul Predictor]
            M3C[Load Matcher]
        end
    end
    
    subgraph "Data Layer"
        DB[(Mission Database)]
        RT[Real-time Feeds]
        ML[ML Models]
    end
    
    D --> M2A
    F --> M1A
    M1A --> M1B --> M1C
    M2A --> M2B --> M2C
    M3A --> M3B --> M3C
    
    M1C --> DB
    M2C --> DB
    M3C --> DB
    
    RT --> M2A
    ML --> M2B
    ML --> M3B
```

### Core Agent Loop

```mermaid
sequenceDiagram
    participant E as Environment
    participant O as Observer
    participant R as Reasoner
    participant A as Actor
    participant U as User
    
    loop Every Decision Cycle (5-15 mins)
        E->>O: Traffic, Load Availability, Fuel Prices
        O->>O: Aggregate & Normalize Data
        O->>R: Processed Context State
        R->>R: Simulate Scenarios
        R->>R: Calculate Opportunity vs Cost
        R->>A: Optimal Decision
        A->>U: Push Notification/Route Update
        A->>E: Execute Action (Accept Load, Reroute)
    end
```

---

## 4. System Architecture

### High-Level Architecture

```mermaid
flowchart TB
    subgraph "Frontend Layer"
        DA[Driver Mobile App<br/>React Native]
        FD[Fleet Dashboard<br/>React/Next.js]
    end
    
    subgraph "API Gateway"
        AG[API Gateway<br/>Rate Limiting, Auth]
    end
    
    subgraph "Backend Services"
        MS[Mission Service]
        RS[Routing Service]
        PS[Pricing Service]
        LS[Load Matching Service]
        NS[Notification Service]
    end
    
    subgraph "Agent Layer"
        AE[Agent Executor<br/>Decision Loop]
        SM[State Manager]
        PE[Policy Engine]
    end
    
    subgraph "Data Layer"
        PG[(PostgreSQL<br/>Missions, Users)]
        RD[(Redis<br/>Real-time State)]
        TS[(TimescaleDB<br/>Telemetry)]
    end
    
    subgraph "External Integrations"
        GM[Google Maps API]
        TF[Traffic Feed]
        FP[Fuel Price API]
        LM[Load Marketplace]
    end
    
    DA --> AG
    FD --> AG
    AG --> MS
    AG --> RS
    AG --> PS
    AG --> LS
    
    MS --> AE
    RS --> AE
    PS --> AE
    LS --> AE
    
    AE --> SM
    AE --> PE
    
    SM --> RD
    PE --> PG
    MS --> TS
    
    RS --> GM
    AE --> TF
    PS --> FP
    LS --> LM
    
    NS --> DA
    NS --> FD
```

### Agent State Machine

```mermaid
stateDiagram-v2
    [*] --> IDLE: System Start
    
    IDLE --> PLANNING: New Mission Request
    PLANNING --> EN_ROUTE: Mission Accepted
    
    EN_ROUTE --> MONITORING: Continuous Loop
    MONITORING --> EVALUATING: Trigger Detected
    
    EVALUATING --> ADAPTING: Decision Made
    EVALUATING --> MONITORING: No Action Needed
    
    ADAPTING --> EN_ROUTE: Route Updated
    ADAPTING --> LOAD_MATCHING: Capacity Available
    
    LOAD_MATCHING --> EN_ROUTE: Load Matched
    LOAD_MATCHING --> EN_ROUTE: No Match Found
    
    EN_ROUTE --> COMPLETING: Near Destination
    COMPLETING --> BACKHAUL_SEARCH: Drop Complete
    
    BACKHAUL_SEARCH --> PLANNING: Return Load Found
    BACKHAUL_SEARCH --> IDLE: No Load / Driver Done
    
    COMPLETING --> [*]: Mission Complete
```

---

## 5. Module Specifications

### Module 1: Context-Aware Mission Planner

```mermaid
flowchart LR
    subgraph "Inputs"
        I1[Origin & Destination]
        I2[Vehicle Specs]
        I3[Load Details]
        I4[Time Constraints]
    end
    
    subgraph "Processing"
        P1[Road Graph Analysis]
        P2[Checkpoint Probability Model]
        P3[Historical Delay Data]
        P4[Fuel Cost Calculator]
    end
    
    subgraph "Outputs"
        O1[Optimized Route]
        O2[Dynamic Fare]
        O3[Risk Score]
        O4[ETA Range]
    end
    
    I1 --> P1
    I2 --> P1
    I3 --> P4
    I4 --> P2
    
    P1 --> O1
    P2 --> O4
    P3 --> O3
    P4 --> O2
```

**Key Features:**
| Feature | Description | Priority |
|---------|-------------|----------|
| Infrastructure-Aware Routing | Considers truck-specific constraints (height, weight, no-entry zones) | P0 |
| Checkpoint Delay Prediction | ML model trained on state border crossing times | P0 |
| Dynamic Fare Calculation | Real-time pricing based on route difficulty, fuel, demand | P0 |
| Risk Assessment | Probability scores for delays, safety concerns | P1 |

### Module 2: Rolling Decision Engine

```mermaid
flowchart TB
    subgraph "Trigger Layer"
        T1[Time-based: Every 15 mins]
        T2[Event-based: Traffic Alert]
        T3[Event-based: New Load Available]
        T4[Event-based: Fuel Price Change]
    end
    
    subgraph "Evaluation Layer"
        E1[Current State Snapshot]
        E2[Scenario Simulation]
        E3[Cost-Benefit Analysis]
    end
    
    subgraph "Decision Layer"
        D1{Positive ROI?}
        D2[Generate New Plan]
        D3[Maintain Current Plan]
    end
    
    subgraph "Action Layer"
        A1[Update Route]
        A2[Notify Driver]
        A3[Log Decision]
    end
    
    T1 --> E1
    T2 --> E1
    T3 --> E1
    T4 --> E1
    
    E1 --> E2 --> E3
    E3 --> D1
    
    D1 -->|Yes| D2
    D1 -->|No| D3
    
    D2 --> A1 --> A2 --> A3
    D3 --> A3
```

**Decision Triggers:**
| Trigger | Threshold | Action |
|---------|-----------|--------|
| Traffic Delay | >20 min deviation | Re-route evaluation |
| New Load Nearby | <15 km detour | Opportunity calculation |
| Fuel Price Spike | >5% increase | Refuel point optimization |
| Weather Alert | Severity > Medium | Safety re-routing |

### Module 3: Dynamic Capacity Manager

```mermaid
flowchart TB
    subgraph "Capacity Monitoring"
        CM1[Current Load: 60%]
        CM2[Available Space: 4 tons]
        CM3[Route Corridor: 50km buffer]
    end
    
    subgraph "Load Discovery"
        LD1[Active Load Board Scan]
        LD2[Partner API Integration]
        LD3[Historical Pattern Match]
    end
    
    subgraph "Matching Engine"
        ME1{Compatible?}
        ME2[Calculate Detour Cost]
        ME3[Calculate Revenue Add]
        ME4{Profitable?}
    end
    
    subgraph "Backhaul Prediction"
        BP1[Destination Market Analysis]
        BP2[Pre-booking Engine]
        BP3[Price Negotiation Bot]
    end
    
    CM1 --> LD1
    CM2 --> LD2
    CM3 --> LD3
    
    LD1 --> ME1
    LD2 --> ME1
    
    ME1 -->|Yes| ME2
    ME1 -->|No| LD1
    
    ME2 --> ME3 --> ME4
    ME4 -->|Yes| BP2
    ME4 -->|No| LD1
    
    BP1 --> BP2 --> BP3
```

**Pooling Logic:**
```
Profitability Score = (Additional Revenue - Detour Cost - Time Cost) / Risk Factor

Where:
- Additional Revenue = Load Rate × Weight
- Detour Cost = Extra Distance × Fuel Rate
- Time Cost = Extra Time × Hourly Opportunity Cost  
- Risk Factor = 1.0 to 1.5 based on load type, shipper rating
```

---

## 6. Data Models

### Entity Relationship Diagram

```mermaid
erDiagram
    USER ||--o{ VEHICLE : owns
    USER ||--o{ MISSION : creates
    USER {
        uuid id PK
        string type "driver|fleet_operator"
        string name
        string phone
        json preferences
        float rating
    }
    
    VEHICLE ||--o{ MISSION : executes
    VEHICLE {
        uuid id PK
        uuid owner_id FK
        string registration_number
        string vehicle_type
        float max_capacity_tons
        float current_fuel_level
        json dimensions
        point current_location
    }
    
    MISSION ||--o{ LOAD : contains
    MISSION ||--o{ WAYPOINT : has
    MISSION ||--o{ DECISION_LOG : generates
    MISSION {
        uuid id PK
        uuid vehicle_id FK
        string status
        point origin
        point destination
        timestamp start_time
        timestamp eta
        float quoted_fare
        float actual_fare
        json route_polyline
    }
    
    LOAD {
        uuid id PK
        uuid mission_id FK
        string shipper_id
        float weight_tons
        string cargo_type
        point pickup_location
        point drop_location
        float rate
        string status
    }
    
    WAYPOINT {
        uuid id PK
        uuid mission_id FK
        int sequence
        point location
        string type "pickup|drop|fuel|rest"
        timestamp eta
        timestamp actual_arrival
    }
    
    DECISION_LOG {
        uuid id PK
        uuid mission_id FK
        timestamp timestamp
        string trigger_type
        json context_snapshot
        json options_evaluated
        string decision_made
        json outcome
    }
    
    CHECKPOINT ||--o{ CHECKPOINT_DELAY : records
    CHECKPOINT {
        uuid id PK
        string name
        point location
        string state_border
        float avg_delay_mins
    }
    
    CHECKPOINT_DELAY {
        uuid id PK
        uuid checkpoint_id FK
        timestamp recorded_at
        float delay_mins
        string day_of_week
        int hour_of_day
    }
```

---

## 7. User Flows

### Flow 1: Driver Journey (Happy Path)

```mermaid
journey
    title Driver Daily Journey with Neuro-Logistics
    section Morning Setup
      Open App: 5: Driver
      View Available Missions: 4: Driver
      Accept Mission to Pune: 5: Driver
      See Dynamic Fare ₹12,500: 5: Driver
    section En Route
      Start Navigation: 5: Driver
      Receive Traffic Alert: 3: System
      Auto-Reroute Suggested: 4: System
      Accept New Route: 5: Driver
    section Mid-Journey
      Agent Finds Gap Load: 5: System
      Notification: +₹2000 opportunity: 5: System
      Accept Additional Pickup: 5: Driver
      Complete Extra Stop: 4: Driver
    section Delivery
      Arrive at Destination: 5: Driver
      Complete Delivery: 5: Driver
      Backhaul Already Booked: 5: System
      Start Return Journey: 5: Driver
```

### Flow 2: Fleet Operator Dashboard

```mermaid
flowchart TB
    subgraph "Dashboard View"
        DV1[Live Fleet Map]
        DV2[Mission Queue]
        DV3[Analytics Panel]
    end
    
    subgraph "Actions"
        A1[Assign New Mission]
        A2[Override Agent Decision]
        A3[Set Fleet Constraints]
        A4[View Earnings Report]
    end
    
    subgraph "Alerts"
        AL1[Delay Notifications]
        AL2[Opportunity Alerts]
        AL3[Vehicle Health Warnings]
    end
    
    DV1 --> A1
    DV1 --> A2
    DV2 --> A1
    DV3 --> A4
    
    AL1 --> DV1
    AL2 --> DV2
    AL3 --> DV1
```

### Flow 3: Agent Decision Cycle

```mermaid
sequenceDiagram
    participant V as Vehicle (In Motion)
    participant A as Agent
    participant L as Load Marketplace
    participant D as Driver App
    participant F as Fleet Dashboard
    
    Note over V,F: Every 15 minutes or on trigger
    
    V->>A: Location, Speed, ETA Update
    A->>A: Check Current Capacity (60%)
    A->>L: Query: Loads within 20km corridor
    L-->>A: 3 Available Loads
    
    A->>A: Filter: Weight ≤ 4 tons
    A->>A: Filter: Route alignment > 70%
    A->>A: Calculate: Best Option ROI
    
    alt Profitable Opportunity Found
        A->>D: Push: "New Load Available"
        A->>D: Details: Pickup Khopoli, +₹2000
        D-->>A: Driver Accepts
        A->>A: Update Mission Plan
        A->>D: New Route with Waypoint
        A->>F: Mission Updated Notification
    else No Viable Opportunity
        A->>A: Log: No action taken
        Note over A: Continue monitoring
    end
```

---

## 8. API Specifications

### Core API Endpoints

```mermaid
graph LR
    subgraph "Mission APIs"
        M1[POST /missions - Create]
        M2[GET /missions/:id - Details]
        M3[PATCH /missions/:id - Update]
        M4[GET /missions/:id/route - Get Route]
    end
    
    subgraph "Vehicle APIs"
        V1[POST /vehicles - Register]
        V2[GET /vehicles/:id/location - Live Location]
        V3[PATCH /vehicles/:id/status - Update Status]
    end
    
    subgraph "Load APIs"
        L1[GET /loads/search - Find Loads]
        L2[POST /loads/:id/match - Match to Mission]
        L3[GET /loads/backhaul - Find Return Loads]
    end
    
    subgraph "Agent APIs"
        A1[GET /agent/decisions/:mission_id - Decision Log]
        A2[POST /agent/override - Manual Override]
        A3[GET /agent/opportunities - Current Opportunities]
    end
```

### Key API Contracts

**POST /missions**
```json
{
  "request": {
    "vehicle_id": "uuid",
    "origin": {"lat": 19.076, "lng": 72.877},
    "destination": {"lat": 18.520, "lng": 73.856},
    "load": {
      "weight_tons": 6,
      "cargo_type": "general",
      "pickup_time": "2026-01-31T08:00:00Z"
    },
    "constraints": {
      "max_detour_km": 30,
      "avoid_tolls": false,
      "preferred_rest_stops": []
    }
  },
  "response": {
    "mission_id": "uuid",
    "route": {
      "polyline": "encoded_string",
      "distance_km": 150,
      "duration_mins": 240,
      "eta_range": {
        "optimistic": "2026-01-31T12:00:00Z",
        "realistic": "2026-01-31T13:30:00Z",
        "pessimistic": "2026-01-31T15:00:00Z"
      }
    },
    "fare": {
      "base": 10000,
      "fuel_surcharge": 1500,
      "difficulty_premium": 1000,
      "total": 12500,
      "breakdown": {}
    },
    "risk_assessment": {
      "overall_score": 0.72,
      "factors": [
        {"type": "checkpoint_delay", "probability": 0.6, "impact_mins": 45},
        {"type": "traffic", "probability": 0.4, "impact_mins": 30}
      ]
    }
  }
}
```

---

## 9. Tech Stack

### Recommended Stack for Hackathon

```mermaid
graph TB
    subgraph "Frontend"
        F1[React Native - Driver App]
        F2[Next.js 14 - Fleet Dashboard]
        F3[TailwindCSS - Styling]
        F4[Mapbox GL - Maps]
    end
    
    subgraph "Backend"
        B1[Node.js + Express/Fastify]
        B2[Python FastAPI - ML Services]
        B3[Socket.io - Real-time]
    end
    
    subgraph "Database"
        D1[PostgreSQL + PostGIS]
        D2[Redis - Caching/Pub-Sub]
    end
    
    subgraph "AI/ML"
        A1[OpenAI GPT-4 - Reasoning]
        A2[Custom Models - Predictions]
    end
    
    subgraph "Infrastructure"
        I1[Vercel - Frontend]
        I2[Railway/Render - Backend]
        I3[Supabase - Database]
    end
    
    F1 --> B1
    F2 --> B1
    B1 --> D1
    B1 --> D2
    B1 --> B2
    B2 --> A1
    B2 --> A2
```

| Layer | Technology | Justification |
|-------|------------|---------------|
| Driver App | React Native + Expo | Cross-platform, fast development |
| Fleet Dashboard | Next.js 14 | SSR, API routes, fast iteration |
| Primary Backend | Node.js + Fastify | High performance, real-time support |
| ML/Agent Service | Python + FastAPI | ML ecosystem, LangChain support |
| Database | PostgreSQL + PostGIS | Spatial queries, reliability |
| Cache/Pub-Sub | Redis | Real-time state, fast lookups |
| Maps | Mapbox/Google Maps | Routing, traffic data |
| AI Reasoning | OpenAI GPT-4 / Claude | Complex decision making |

---

## 10. File Structure

### Project Structure

```
neuro-logistics/
├── apps/
│   ├── driver-app/              # React Native Driver App
│   │   ├── src/
│   │   │   ├── screens/
���   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── services/
│   │   │   └── navigation/
│   │   └── app.json
│   │
│   └── fleet-dashboard/         # Next.js Fleet Dashboard
│       ├── app/
│       │   ├── dashboard/
│       │   ├── missions/
│       │   ├── vehicles/
│       │   └── analytics/
│       ├── components/
│       └── lib/
│
├── services/
│   ├── api-gateway/             # Main API Service
│   │   ├── src/
│   │   │   ├── routes/
│   │   │   ├── controllers/
│   │   │   ├── middleware/
│   │   │   └── utils/
│   │   └── package.json
│   │
│   ├── agent-service/           # Python Agent/ML Service
│   │   ├── app/
│   │   │   ├── agent/
│   │   │   │   ├── executor.py
│   │   │   │   ├── state.py
│   │   │   │   └── policies.py
│   │   │   ├── models/
│   │   │   ├── services/
│   │   │   └── api/
│   │   └── requirements.txt
│   │
│   └── notification-service/    # Push Notifications
│
├── packages/
│   └── shared/                  # Shared types, utilities
│       ├── types/
│       └── utils/
│
├── database/
│   ├── migrations/
│   └── seeds/
│
├── docs/
│   └── PRD.md
│
└── docker-compose.yml
```

---

## 11. Development Phases

### Hackathon 24-Hour Timeline

```mermaid
gantt
    title Neuro-Logistics 24-Hour Development Plan
    dateFormat HH:mm
    axisFormat %H:%M
    
    section Phase 1: Foundation (0-6 hrs)
    Project Setup & DB Schema           :p1, 00:00, 2h
    Core API Endpoints                  :p2, after p1, 2h
    Basic Driver App UI                 :p3, after p1, 3h
    Fleet Dashboard Shell               :p4, 02:00, 2h
    
    section Phase 2: Core Features (6-14 hrs)
    Mission Planner Module              :p5, 06:00, 3h
    Dynamic Fare Engine                 :p6, after p5, 2h
    Route Optimization                  :p7, 06:00, 3h
    Real-time Location Tracking         :p8, after p7, 2h
    
    section Phase 3: Agent Intelligence (14-20 hrs)
    Decision Engine Loop                :p9, 14:00, 3h
    Load Matching Algorithm             :p10, after p9, 2h
    Backhaul Prediction                 :p11, 17:00, 2h
    Notification System                 :p12, after p10, 1h
    
    section Phase 4: Polish (20-24 hrs)
    Integration Testing                 :p13, 20:00, 2h
    UI Polish & Demo Flow               :p14, after p13, 1h
    Demo Preparation                    :p15, 23:00, 1h
```

### MVP Feature Priority

| Priority | Feature | Time Estimate |
|----------|---------|---------------|
| P0 | Basic Mission Creation & Route Display | 3 hrs |
| P0 | Dynamic Fare Calculation | 2 hrs |
| P0 | Real-time Vehicle Tracking | 2 hrs |
| P0 | Agent Decision Loop (Basic) | 3 hrs |
| P1 | Load Matching for LTL | 2 hrs |
| P1 | Backhaul Suggestion | 2 hrs |
| P1 | Fleet Dashboard Overview | 2 hrs |
| P2 | Checkpoint Delay Prediction | 2 hrs |
| P2 | Historical Analytics | 2 hrs |

---

## 12. Success Metrics

### Demo Metrics (For Hackathon Judging)

```mermaid
pie title Value Demonstration Split
    "Route Optimization" : 25
    "Dynamic Pricing" : 20
    "Real-time Adaptation" : 25
    "Load Matching" : 20
    "User Experience" : 10
```

### KPIs to Showcase

| Metric | Demo Scenario | Expected Output |
|--------|---------------|-----------------|
| Route Efficiency | Mumbai → Pune trip | Shows checkpoint-aware routing saving 45 mins |
| Dynamic Pricing | Same trip, different times | Fare varies by ₹800-1500 based on conditions |
| Adaptation | Simulate traffic jam | Agent reroutes within 30 seconds |
| Load Matching | 60% capacity truck | Finds gap-filler load, +₹2000 revenue |
| Backhaul | Approaching destination | Pre-booked return load displayed |

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **Agentic System** | AI system that can autonomously observe, reason, and act |
| **Backhaul** | Return journey load to avoid empty miles |
| **Dead Mile** | Distance traveled without cargo (unprofitable) |
| **LTL** | Less Than Truckload - partial capacity shipments |
| **Mission** | A complete trip from origin to destination with all waypoints |
| **Rolling Decision** | Continuous re-evaluation while in motion |

---

## Appendix B: External API Dependencies

| API | Purpose | Fallback |
|-----|---------|----------|
| Google Maps Directions | Route calculation | OpenRouteService |
| Google Maps Traffic | Real-time traffic | Historical patterns |
| OpenAI GPT-4 | Complex reasoning | Rule-based decisions |
| Fuel Price API | Dynamic fuel costs | Last known + 5% buffer |

---

*Document Version: 1.0 | Last Updated: January 31, 2026*