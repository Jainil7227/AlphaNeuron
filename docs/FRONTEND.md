# Neuro-Logistics: Frontend Design Specification for Bolt

## 1. Project Overview
**Name:** Neuro-Logistics
**Tagline:** The AI Co-Pilot for Intelligent Logistics Operations
**Core Value:** Transforming static delivery plans into fluid, agentic operations using three intelligent modules (Planner, Rolling Decision Engine, Capacity Manager).

## 2. Tech Stack & Environment
- **Framework:** React 18 + Vite (TypeScript)
- **Styling:** Tailwind CSS (v3.4+)
- **State Management:** Zustand
- **Icons:** Lucide-React
- **Maps:** React-Leaflet or Mapbox GL
- **Charts:** Recharts
- **Animation:** Framer Motion (for "wow" factor)
- **Runtime:** Node.js (v20+)

---

## 3. Design Aesthetics & System
**Theme:** "Future of Logistics" - sleek, professional, high-contrast, data-rich but not cluttered.

### Color Palette
- **Primary (Neuro Blue):** `#2563EB` (Core actions, branding)
- **Secondary (Slate):** `#0F172A` (Sidebars, headers)
- **Accent (Signal Amber):** `#F59E0B` (Alerts, warnings, opportunities)
- **Success (Profit Green):** `#10B981` (Positive revenue, safe routes)
- **Danger (Risk Red):** `#EF4444` (Critical delays, losses)
- **Background:** `#F8FAFC` (Light mode base), `#1E293B` (Cards/Panels in dark mode)

### Typography
- **Headings:** Inter or Space Grotesk (Modern, legible)
- **Body:** Inter (Clean, standard)
- **Monospace:** JetBrains Mono (For numbers, coordinates, prices)

### UI Components (Glassmorphism & Card-Based)
All major data points should be presented in "Cards" with subtle shadows and rounded corners (`rounded-xl`, `shadow-sm`).
- **Glass Effects:** Use `backdrop-blur-md` and `bg-white/80` for overlays on maps.
- **Micro-interactions:** Buttons scale down slightly on click (`active:scale-95`). Hover effects on cards (`hover:-translate-y-1`).

---

## 4. User Interfaces & Layouts

### A. Driver Interface (Mobile-First)
*Target Device: Mobile Browser (Responsive)*

**Layout:**
- **Top Bar:** Hamburger menu, Status Toggle (Online/Offline), Notifications.
- **Main View:** Split screen or Toggle-able Map/List view.
- **Bottom Bar:** Quick Actions (Nav, Load, Earnings).

**Key Screens:**
1.  **Mission Dashboard (Home):**
    - **Header:** "Good Morning, [Name]".
    - **Active Mission Card:** Large card showing current destination, ETA, and "Navigate" button.
    - **Stats Row:** Today's Earnings, Kilometers driven.
2.  **Live Mission Mode (The Co-Pilot):**
    - **Map Background:** Full-screen map with route line.
    - **Dynamic Overlay (Agents):**
        - *Top:* Next Checkpoint & ETA.
        - *Bottom Sheet:* "Agent Insight" - e.g., "Traffic ahead (+15m). Reroute available? (Save 10m)".
3.  **Opportunity Alert (Modal/Overlay):**
    - **Visual:** Pulsing Amber border.
    - **Content:** "New Load Match Detected!"
    - **Details:** "Pickup: 5km away | Extra Pay: ₹2,500 | Detour: +15 mins".
    - **Actions:** "Accept (Swipe Right)" vs "Reject".

### B. Fleet Operator Interface (Desktop-First)
*Target Device: Desktop / Laptop*

**Layout:**
- **Sidebar:** Navigation (Dashboard, Maps, Missions, Vehicles, Analytics).
- **Main Canvas:** Data-heavy, dashboard style.

**Key Screens:**
1.  **Command Center (Dashboard):**
    - **Global Map:** All vehicles plotted real-time. Color-coded by status (Moving=Green, Stopped=Red, Idle=Grey).
    - **KPI Cards:** Total Active Missions, Revenue Today, Fleet Utilization %.
2.  **Mission Planner (Module 1):**
    - **Input:** Origin, Destination, Cargo Type.
    - **Output (AI Generated):** 
        - Show 3 Route Options: "Fastest", "Cheapest", "Safest".
        - *Smart Pricing:* Breakdown of costs (Fuel, Tolls, Driver) + Margin = Quoted Price.
3.  **Live Monitoring:**
    - Sidebar list of active missions. Clicking one zooms the map to that truck.
    - **Agent Log:** A feed showing AI decisions made for that truck (e.g., "Auto-rerouted at 14:00 due to accident").

---

## 5. Core Feature Implementation Specs

### Module 1: Context-Aware Mission Planner
**Visual Element:** "The Strategy Canvas"
- **Input:** standard form.
- **Visualization:** Map showing route with "Risk Zones" highlighted (e.g., Red segment for "High Theft Area" or "Congestion").
- **Quote Card:** Dynamically updates price as user adjusts route preferences.

### Module 2: Rolling Decision Engine
**Visual Element:** "The Agent Feed"
- On the Driver/Fleet dashboard, a timeline component.
- **Items:**
    - 🟢 10:00 AM - Mission Started.
    - 🟡 11:30 AM - Traffic Detected (Delay +20m).
    - 🔵 11:31 AM - AI Suggested Reroute via Highway 44.
    - ✅ 11:32 AM - Driver Accepted Reroute.

### Module 3: Dynamic Capacity Manager
**Visual Element:** "Load Tetris" & "Backhaul Radar"
- **Capacity Indicator:** A truck visual showing 60% full (Green) and 40% empty (Grey).
- **Match Suggestion:** A card appearing when capacity < 100%. "Found LTL Load: 500kg Electronics. Matches your route. +₹4000."
- **Backhaul Finder:** Auto-searches for return trips near the destination before arrival.

---

## 6. Bolt Prompt (Copy & Paste)
*Use this prompt to generate the foundation of the app.*

```text
Build a modern, responsive React + TypeScript application for "Neuro-Logistics", an AI-powered logistics platform.

**Tech Stack:** React 18, Vite, TailwindCSS, Lucide React (icons), React Router v6, Zustand (store), Recharts, React-Leaflet.

**Design System:**
- Use a professional "Logistics Blue" (#2563EB) and "Slate" dark theme.
- Implement Glassmorphism for dashboard cards.
- Mobile-responsive is critical for driver views.

**Core Features to Build:**

1.  **Navigation Structure:**
    - Landing Page (Public)
    - /driver (Mobile layout with bottom nav)
    - /fleet (Desktop layout with sidebar)

2.  **Driver Dashboard (/driver):**
    - Show "Active Mission" card with Map placeholder.
    - Implement an "Agent Alert" component that pops up with "New Opportunity" (Accept/Reject).
    - "Earnings" widget.

3.  **Fleet Dashboard (/fleet):**
    - "Live Map" view showing multiple vehicle markers.
    - "Mission Planner" form: Inputs for Start/End -> Generates 3 Route Cards (Optimistic, Realistic, Pessimistic) with different prices.
    - "Analytics" chart showing Revenue vs Cost (use Recharts).

4.  **Mock Data:**
    - Create a store (Zustand) with mock active missions, vehicles, and alerts.
    - Simulate "Live Updates" using `setInterval` to move truck markers on the map.

**Specific UI Requirements:**
- Use `framer-motion` for smooth transitions between pages and alerts.
- Ensure the "Opportunity Alert" looks urgent and actionable (Swipe/Tap).
- The "Mission Planner" should visually break down the Fare (Base + Fuel + Risk Premium).

Start by setting up the routing and the main layout shells for Driver and Fleet.
```