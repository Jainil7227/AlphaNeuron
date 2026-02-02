/**
 * Neuro-Logistics API Service
 * 
 * Connects the frontend to the backend API.
 * All 3 modules are covered:
 * - Module 1: Mission Planner
 * - Module 2: Decision Engine
 * - Module 3: Capacity Manager
 */

// Use environment variable for API URL in production, fallback to localhost for dev
const API_BASE_URL = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api`
  : 'http://localhost:8000/api';

// ==========================================
// TYPES
// ==========================================

export interface MissionPlanRequest {
  origin: string;
  destination: string;
  cargo_type: string;
  weight_tons: number;
  vehicle_id?: string;
}

export interface MissionPlan {
  mission_id: string | null;
  origin: string;
  destination: string;
  cargo: {
    type: string;
    weight_tons: number;
  };
  route: {
    distance_km: number;
    highways: string[];
    toll_plazas: number;
    toll_cost: number;
    checkpoints: string[];
    fuel_stops: number;
    is_estimated: boolean;
  };
  eta_range: {
    optimistic: { hours: number; arrival: string };
    expected: { hours: number; arrival: string };
    pessimistic: { hours: number; arrival: string };
  };
  fare: {
    calculated: {
      base_fare: number;
      effort_multiplier: number;
      adjusted_base: number;
      toll_cost: number;
      fuel_estimate: number;
      driver_allowance: number;
      total_fare: number;
      per_km_rate: number;
    };
    ai_recommended: any;
  };
  risk_assessment: {
    score: number;
    level: string;
    factors: string[];
    recommendations: string[];
  };
  ai_insights: any;
  return_load_options: any[];
  created_at: string;
}

export interface EvaluateSituationRequest {
  mission_id: string;
  current_location: string;
  conditions?: Record<string, any>;
}

export interface DecisionResult {
  mission_id: string;
  observation: {
    progress_percent: number;
    conditions: {
      traffic: string;
      weather: string;
      fuel_level_percent: number;
      driver_fatigue_level: string;
    };
    nearby_opportunities: any[];
  };
  ai_analysis: {
    recommended_action: string;
    situation_assessment: string;
    observations: string[];
    risks: string[];
    opportunities: string[];
  };
  decision: {
    action: string;
    confidence: number;
    reasons: string[];
    alerts: any[];
    opportunities_found: number;
  };
  timestamp: string;
}

export interface LTLMatchResult {
  mission_id: string;
  current_route: string;
  capacity: {
    total_tons: number;
    current_load_tons: number;
    available_tons: number;
    utilization_percent: number;
  };
  available_loads: any[];
  ai_recommendations: any;
  summary: {
    loads_found: number;
    total_potential_revenue: number;
    utilization_after_pooling: number;
  };
}

export interface BackhaulResult {
  mission_id: string;
  current_destination: string;
  home_base: string;
  return_journey: {
    distance_km: number;
    estimated_hours: number;
  };
  empty_return_cost: {
    fuel_cost: number;
    toll_cost: number;
    driver_cost: number;
    total: number;
  };
  backhaul_options: any[];
  ai_recommendation: any;
  savings_summary: {
    without_backhaul: number;
    with_best_backhaul: number;
    potential_profit: number;
  };
}

export interface Vehicle {
  id: string;
  registration: string;
  type: string;
  capacity_tons: number;
  current_load_tons: number;
  driver_name: string;
  driver_phone: string;
  current_city: string;
  status: string;
  fuel_level_percent: number;
}

export interface Mission {
  id: string;
  status: string;
  origin: string;
  destination: string;
  cargo: { type: string; weight_tons: number };
  route: any;
  progress_percent: number;
  current_location: string;
  created_at: string;
  started_at?: string;
}

export interface CapacityOverview {
  total_active_missions: number;
  fleet_capacity: {
    total_tons: number;
    used_tons: number;
    available_tons: number;
    utilization_percent: number;
  };
  missions: any[];
  recommendations: any[];
}

// ==========================================
// API FUNCTIONS
// ==========================================

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Unknown error' }));
    throw new Error(error.detail || error.error || 'API request failed');
  }

  return response.json();
}

// ==========================================
// HEALTH & ROUTES
// ==========================================

export async function checkHealth() {
  return fetchAPI<{ status: string; version: string; modules: Record<string, string> }>('/health');
}

export async function getRoutes() {
  return fetchAPI<{ success: boolean; cities: string[]; popular_routes: any[] }>('/routes');
}

export async function getRouteDetails(origin: string, destination: string) {
  return fetchAPI<{ success: boolean; route: any }>(`/routes/${encodeURIComponent(origin)}/${encodeURIComponent(destination)}`);
}

// ==========================================
// MODULE 1: MISSION PLANNER
// ==========================================

export async function planMission(request: MissionPlanRequest) {
  return fetchAPI<{ success: boolean; plan: MissionPlan }>('/mission/plan', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export async function startMission(planId: string, vehicleId: string) {
  return fetchAPI<{ success: boolean; message: string }>(`/mission/${planId}/start`, {
    method: 'POST',
    body: JSON.stringify({ vehicle_id: vehicleId }),
  });
}

export async function getMission(missionId: string) {
  return fetchAPI<{ success: boolean; mission: Mission }>(`/mission/${missionId}`);
}

export async function listMissions(status?: string) {
  const query = status ? `?status=${status}` : '';
  return fetchAPI<{ success: boolean; count: number; missions: Mission[] }>(`/missions${query}`);
}

// ==========================================
// MODULE 2: DECISION ENGINE
// ==========================================

export async function evaluateSituation(request: EvaluateSituationRequest) {
  return fetchAPI<{ success: boolean; evaluation: DecisionResult }>('/decision/evaluate', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export async function evaluateOpportunity(missionId: string, opportunity: any) {
  return fetchAPI<{ success: boolean; evaluation: any }>('/decision/opportunity', {
    method: 'POST',
    body: JSON.stringify({ mission_id: missionId, opportunity }),
  });
}

export async function getRerouteOptions(missionId: string, reason: string = 'traffic') {
  return fetchAPI<{ success: boolean; reroute_options: any }>('/decision/reroute', {
    method: 'POST',
    body: JSON.stringify({ mission_id: missionId, reason }),
  });
}

export async function getDecisionHistory(missionId: string) {
  return fetchAPI<{ success: boolean; mission_id: string; decision_count: number; history: any[] }>(
    `/decision/${missionId}/history`
  );
}

// ==========================================
// MODULE 3: CAPACITY MANAGER
// ==========================================

export async function findLTLMatches(missionId: string) {
  return fetchAPI<{ success: boolean; ltl_matches: LTLMatchResult }>('/capacity/ltl-matches', {
    method: 'POST',
    body: JSON.stringify({ mission_id: missionId }),
  });
}

export async function findBackhaul(missionId: string, homeBase?: string) {
  return fetchAPI<{ success: boolean; backhaul_options: BackhaulResult }>('/capacity/backhaul', {
    method: 'POST',
    body: JSON.stringify({ mission_id: missionId, home_base: homeBase }),
  });
}

export async function acceptLTLLoad(missionId: string, loadId: string) {
  return fetchAPI<{ success: boolean; mission_id: string; load_added: any; updated_capacity: any }>(
    '/capacity/pool',
    {
      method: 'POST',
      body: JSON.stringify({ mission_id: missionId, load_id: loadId }),
    }
  );
}

export async function bookBackhaul(missionId: string, loadId: string) {
  return fetchAPI<{ success: boolean; mission_id: string; backhaul_booked: any; message: string }>(
    '/capacity/book-backhaul',
    {
      method: 'POST',
      body: JSON.stringify({ mission_id: missionId, load_id: loadId }),
    }
  );
}

export async function getCapacityOverview() {
  return fetchAPI<{ success: boolean; overview: CapacityOverview }>('/capacity/overview');
}

// ==========================================
// DATA ENDPOINTS
// ==========================================

export async function getLoads(loadType?: string, maxWeight?: number) {
  const params = new URLSearchParams();
  if (loadType) params.append('load_type', loadType);
  if (maxWeight) params.append('max_weight', maxWeight.toString());
  const query = params.toString() ? `?${params.toString()}` : '';
  return fetchAPI<{ success: boolean; count: number; loads: any[] }>(`/loads${query}`);
}

export async function getVehicles(city?: string) {
  const query = city ? `?city=${encodeURIComponent(city)}` : '';
  return fetchAPI<{ success: boolean; count: number; vehicles: Vehicle[] }>(`/vehicles${query}`);
}

export async function getVehicle(vehicleId: string) {
  return fetchAPI<{ success: boolean; vehicle: Vehicle }>(`/vehicle/${vehicleId}`);
}

// ==========================================
// DEMO ENDPOINTS
// ==========================================

export async function getDemoScenario() {
  return fetchAPI<{ success: boolean; scenario: any }>('/demo/scenario');
}

export async function resetDemoData() {
  return fetchAPI<{ success: boolean; message: string }>('/demo/reset', {
    method: 'POST',
  });
}

// ==========================================
// COPILOT CHAT
// ==========================================

export interface CopilotChatRequest {
  mission_id: string;
  query: string;
  context?: Record<string, any>;
}

export interface CopilotChatResponse {
  success: boolean;
  mission_id: string;
  query: string;
  response: string;
  context: {
    progress: number;
    location: string;
    destination: string;
  };
}

export async function copilotChat(request: CopilotChatRequest) {
  return fetchAPI<CopilotChatResponse>('/copilot/chat', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

