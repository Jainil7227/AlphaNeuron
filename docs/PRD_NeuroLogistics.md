# Neuro-Logistics - Product Requirements Document (Web)

## 1. Executive Summary

**Product Name:** Neuro-Logistics  
**Platform:** Web Application (React)  
**Hackathon:** 24-hour Build  

**Problem:** Road logistics is planned as isolated trips. Load matching, routing, and pricing are decided upfront with little ability to adapt. Trucks run underutilized or return empty.

**Solution:** AI-driven agentic system that treats trucking as a continuous operation with three intelligent modules.

---

## 2. Target Users

| User Type | Description | Primary Device |
|-----------|-------------|----------------|
| **Driver** | Individual truck drivers | Mobile browser (responsive) |
| **Fleet Operator** | Manages multiple vehicles | Desktop browser |
| **Admin** | System administrator | Desktop browser |

---

## 3. Three Core Modules

### Module 1: Context-Aware Mission Planner
- Infrastructure-aware routing (toll plazas, checkposts, no-entry timings)
- Dynamic fare calculation based on real-time difficulty
- Risk assessment with optimistic/realistic/pessimistic ETA

### Module 2: Rolling Decision Engine
- Continuous monitoring loop while vehicle is in motion
- Opportunity vs Cost calculator for deviations
- Autonomous rerouting suggestions based on conditions

### Module 3: Dynamic Capacity Manager
- En-route LTL (Less Than Truckload) pooling
- Predictive backhauling to eliminate empty returns
- Real-time load matching with nearby opportunities

---

## 4. Tech Stack

### Frontend (Web)
| Technology | Purpose |
|------------|---------|
| React 18 | UI Framework |
| Vite | Build tool (fast HMR) |
| TypeScript | Type safety |
| TailwindCSS | Styling |
| Zustand | State management |
| React Router v6 | Navigation |
| React-Leaflet | Maps (OpenStreetMap) |
| Socket.io-client | Real-time WebSocket |
| React Query | API caching |
| React Hook Form | Form handling |
| Recharts | Analytics charts |

### Backend (Python - No Changes)
| Technology | Purpose |
|------------|---------|
| FastAPI | REST API Framework |
| PostgreSQL + PostGIS | Database with geospatial |
| SQLAlchemy | ORM |
| Redis | Caching, Pub/Sub |
| Celery | Background tasks |
| python-jose | JWT Authentication |

---

## 5. User Flows

### 5.1 Driver Flow (Mobile-Responsive Web)
```
Login → Dashboard → View Assigned Mission → Start Mission
    → Real-time Map Tracking → Receive Agent Alerts
    → Accept/Reject Opportunities → Complete Delivery
    → View Earnings Summary
```

### 5.2 Fleet Operator Flow (Desktop Web)
```
Login → Fleet Dashboard → View All Vehicles on Map
    → Create New Mission → Assign Driver & Vehicle
    → Monitor Active Missions → Review Agent Decisions
    → View Analytics & Reports
```

---

## 6. Frontend File Structure (Web)

```
frontend/
├── public/
│   ├── favicon.ico
│   └── manifest.json
├── src/
│   ├── assets/
│   │   ├── images/
│   │   └── styles/
│   │       └── globals.css
│   ├── components/
│   │   ├── common/
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Loader.tsx
│   │   │   ├── Badge.tsx
│   │   │   └── index.ts
│   │   ├── layout/
│   │   │   ├── Navbar.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Layout.tsx
│   │   │   ├── MobileNav.tsx
│   │   │   └── index.ts
│   │   ├── maps/
│   │   │   ├── MapContainer.tsx
│   │   │   ├── VehicleMarker.tsx
│   │   │   ├── RoutePolyline.tsx
│   │   │   ├── CheckpointMarker.tsx
│   │   │   └── index.ts
│   │   ├── mission/
│   │   │   ├── MissionCard.tsx
│   │   │   ├── MissionForm.tsx
│   │   │   ├── MissionTimeline.tsx
│   │   │   ├── FareBreakdown.tsx
│   │   │   ├── RiskAssessment.tsx
│   │   │   └── index.ts
│   │   ├── vehicle/
│   │   │   ├── VehicleCard.tsx
│   │   │   ├── VehicleForm.tsx
│   │   │   ├── CapacityIndicator.tsx
│   │   │   └── index.ts
│   │   ├── load/
│   │   │   ├── LoadCard.tsx
│   │   │   ├── LoadMatchSuggestion.tsx
│   │   │   ├── BackhaulCard.tsx
│   │   │   └── index.ts
│   │   ├── agent/
│   │   │   ├── AgentDecisionCard.tsx
│   │   │   ├── OpportunityAlert.tsx
│   │   │   ├── CostBenefitChart.tsx
│   │   │   └── index.ts
│   │   └── analytics/
│   │       ├── RevenueChart.tsx
│   │       ├── UtilizationGauge.tsx
│   │       ├── TripStats.tsx
│   │       └── index.ts
│   ├── pages/
│   │   ├── Landing.tsx
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── NotFound.tsx
│   │   ├── driver/
│   │   │   ├── DriverDashboard.tsx
│   │   │   ├── ActiveMission.tsx
│   │   │   ├── MissionHistory.tsx
│   │   │   ├── AvailableLoads.tsx
│   │   │   └── Earnings.tsx
│   │   ├── fleet/
│   │   │   ├── FleetDashboard.tsx
│   │   │   ├── FleetMap.tsx
│   │   │   ├── MissionPlanner.tsx
│   │   │   ├── MissionList.tsx
│   │   │   ├── VehicleManagement.tsx
│   │   │   ├── DriverManagement.tsx
│   │   │   └── Analytics.tsx
│   │   └── shared/
│   │       └── MissionDetails.tsx
│   ├── services/
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   ├── auth.api.ts
│   │   │   ├── mission.api.ts
│   │   │   ├── vehicle.api.ts
│   │   │   ├── load.api.ts
│   │   │   ├── agent.api.ts
│   │   │   └── index.ts
│   │   └── socket/
│   │       ├── socketClient.ts
│   │       └── index.ts
│   ├── stores/
│   │   ├── authStore.ts
│   │   ├── missionStore.ts
│   │   ├── vehicleStore.ts
│   │   ├── loadStore.ts
│   │   └── index.ts
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useMission.ts
│   │   ├── useVehicle.ts
│   │   ├── useSocket.ts
│   │   ├── useGeolocation.ts
│   │   └── index.ts
│   ├── types/
│   │   ├── auth.types.ts
│   │   ├── mission.types.ts
│   │   ├── vehicle.types.ts
│   │   ├── load.types.ts
│   │   ├── agent.types.ts
│   │   └── index.ts
│   ├── utils/
│   │   ├── constants.ts
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   ├── helpers.ts
│   │   └── index.ts
│   ├── config/
│   │   ├── env.ts
│   │   └── routes.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── router.tsx
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
├── tsconfig.json
├── tsconfig.node.json
└── .env.example
```

---

## 7. API Endpoints (Backend - Unchanged)

### Authentication
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/me`

### Missions
- `GET /api/v1/missions`
- `POST /api/v1/missions`
- `GET /api/v1/missions/:id`
- `PATCH /api/v1/missions/:id`
- `PATCH /api/v1/missions/:id/status`

### Vehicles
- `GET /api/v1/vehicles`
- `POST /api/v1/vehicles`
- `GET /api/v1/vehicles/:id`
- `PATCH /api/v1/vehicles/:id`
- `PATCH /api/v1/vehicles/:id/location`

### Loads
- `GET /api/v1/loads/search`
- `POST /api/v1/loads`
- `GET /api/v1/loads/:id`
- `POST /api/v1/loads/:id/match`
- `GET /api/v1/loads/backhaul`

### Agent
- `GET /api/v1/agent/opportunities/:missionId`
- `POST /api/v1/agent/decisions/:id/accept`
- `POST /api/v1/agent/decisions/:id/reject`

### WebSocket
- `WS /ws` - Real-time updates

---

## 8. Page Descriptions

### Public Pages
| Page | Route | Description |
|------|-------|-------------|
| Landing | `/` | Hero, features, CTA |
| Login | `/login` | Email/phone + password |
| Register | `/register` | User type selection + form |

### Driver Pages (Mobile-Responsive)
| Page | Route | Description |
|------|-------|-------------|
| Dashboard | `/driver` | Today's missions, stats |
| Active Mission | `/driver/mission/:id` | Map, status, agent alerts |
| History | `/driver/history` | Past missions |
| Available Loads | `/driver/loads` | LTL opportunities |
| Earnings | `/driver/earnings` | Revenue breakdown |

### Fleet Operator Pages (Desktop)
| Page | Route | Description |
|------|-------|-------------|
| Dashboard | `/fleet` | Overview, KPIs |
| Fleet Map | `/fleet/map` | All vehicles live |
| Mission Planner | `/fleet/missions/new` | Create mission |
| Mission List | `/fleet/missions` | All missions |
| Vehicles | `/fleet/vehicles` | Vehicle management |
| Drivers | `/fleet/drivers` | Driver management |
| Analytics | `/fleet/analytics` | Charts, reports |

---

## 9. Responsive Design Breakpoints

```css
/* TailwindCSS Default Breakpoints */
sm: 640px   /* Mobile landscape */
md: 768px   /* Tablet */
lg: 1024px  /* Desktop */
xl: 1280px  /* Large desktop */
2xl: 1536px /* Extra large */
```

### Design Approach
- **Driver pages:** Mobile-first, works on phone browsers
- **Fleet pages:** Desktop-first with tablet support
- **Shared components:** Fully responsive

---

## 10. Key Web-Specific Features

### Browser Geolocation
```typescript
// Using native browser API
navigator.geolocation.watchPosition(
  (position) => {
    updateLocation(position.coords.latitude, position.coords.longitude);
  },
  (error) => console.error(error),
  { enableHighAccuracy: true, maximumAge: 10000 }
);
```

### Browser Notifications
```typescript
// Request permission and show notifications
if (Notification.permission === 'granted') {
  new Notification('New Load Match!', {
    body: 'A profitable load is available near your route',
    icon: '/logo.png'
  });
}
```

### PWA Support (Optional)
- Service worker for offline capability
- manifest.json for "Add to Home Screen"
- Works like native app on mobile

---

## 11. Deployment

| Service | Purpose | Free Tier |
|---------|---------|-----------|
| Vercel | Frontend hosting | Yes |
| Railway | Backend + PostgreSQL | Yes |
| Upstash | Redis | Yes |
| Cloudflare | CDN + Domain | Yes |

---

## 12. Demo Script (5 minutes)

1. **Landing Page** (30s) - Show problem statement
2. **Fleet Operator Login** (30s) - Desktop view
3. **Create Mission** (60s) - Module 1: Route planning, fare, risk
4. **Fleet Map** (30s) - Show vehicle tracking
5. **Driver View** (60s) - Mobile browser, active mission
6. **Agent Alert** (60s) - Module 2: Show opportunity, cost-benefit
7. **Accept Load Match** (30s) - Module 3: LTL pooling
8. **Analytics** (30s) - Revenue increase visualization