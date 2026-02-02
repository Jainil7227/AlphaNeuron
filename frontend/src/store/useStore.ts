import { create } from 'zustand';
import * as api from '../services/api';

// ==========================================
// TYPES
// ==========================================

export interface Vehicle {
  id: string;
  registration: string;
  driverName: string;
  vehicleNumber: string;
  lat: number;
  lng: number;
  status: 'moving' | 'stopped' | 'idle' | 'available' | 'in_transit';
  currentMission?: string;
  capacity_tons: number;
  current_load_tons: number;
}

export interface Mission {
  id: string;
  vehicleId?: string;
  origin: string;
  destination: string;
  status: 'active' | 'completed' | 'planned' | 'in_progress';
  progress: number;
  eta: string;
  cargo: string;
  cargoType: string;
  weightTons: number;
  distance: number;
  revenue: number;
  riskLevel: string;
  currentLocation?: string;
}

export interface Alert {
  id: string;
  type: 'opportunity' | 'warning' | 'reroute' | 'ltl' | 'backhaul';
  title: string;
  message: string;
  pickup?: string;
  extraPay?: number;
  detour?: string;
  timestamp: Date;
  data?: any;
}

export interface AgentLog {
  id: string;
  time: string;
  type: 'info' | 'warning' | 'success' | 'reroute' | 'decision';
  message: string;
}

export interface MissionPlan {
  origin: string;
  destination: string;
  cargo: { type: string; weight_tons: number };
  route: any;
  eta_range: any;
  fare: any;
  risk_assessment: any;
  ai_insights: any;
  return_load_options: any[];
}

export interface CapacityInfo {
  total_tons: number;
  current_load_tons: number;
  available_tons: number;
  utilization_percent: number;
}

export interface LTLMatch {
  id: string;
  cargo_type: string;
  weight_tons: number;
  pickup_city: string;
  delivery_city: string;
  offered_rate: number;
  urgency: string;
}

export interface BackhaulOption {
  id: string;
  cargo_type: string;
  weight_tons: number;
  pickup_city: string;
  delivery_city: string;
  offered_rate: number;
}

interface StoreState {
  // Data
  vehicles: Vehicle[];
  missions: Mission[];
  alerts: Alert[];
  agentLogs: AgentLog[];
  driverEarnings: number;
  fleetRevenue: number;
  cities: string[];

  // Current state
  currentMissionPlan: MissionPlan | null;
  currentMissionId: string | null;
  currentDecision: any | null;
  ltlMatches: LTLMatch[];
  backhaulOptions: BackhaulOption[];
  capacityInfo: CapacityInfo | null;

  // Loading states
  loading: boolean;
  error: string | null;

  // API Actions
  fetchRoutes: () => Promise<void>;
  fetchVehicles: () => Promise<void>;
  fetchMissions: () => Promise<void>;

  // Module 1: Mission Planner
  planNewMission: (origin: string, destination: string, cargoType: string, weightTons: number) => Promise<MissionPlan | null>;
  startMission: (vehicleId: string) => Promise<boolean>;

  // Module 2: Decision Engine
  evaluateSituation: (missionId: string, location: string) => Promise<any>;
  evaluateOpportunity: (missionId: string, opportunity: any) => Promise<any>;

  // Module 3: Capacity Manager
  findLTLMatches: (missionId: string) => Promise<void>;
  findBackhaul: (missionId: string, homeBase?: string) => Promise<void>;
  acceptLTLLoad: (missionId: string, loadId: string) => Promise<boolean>;
  bookBackhaul: (missionId: string, loadId: string) => Promise<boolean>;
  getCapacityOverview: () => Promise<any>;

  // Demo
  loadDemoScenario: () => Promise<void>;
  resetDemo: () => Promise<void>;

  // Local actions
  updateVehiclePosition: (id: string, lat: number, lng: number) => void;
  addAlert: (alert: Alert) => void;
  removeAlert: (id: string) => void;
  addAgentLog: (log: AgentLog) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

// City coordinates for map display
const CITY_COORDS: Record<string, { lat: number; lng: number }> = {
  'Mumbai': { lat: 19.076, lng: 72.8777 },
  'Delhi': { lat: 28.7041, lng: 77.1025 },
  'Bangalore': { lat: 12.9716, lng: 77.5946 },
  'Chennai': { lat: 13.0827, lng: 80.2707 },
  'Kolkata': { lat: 22.5726, lng: 88.3639 },
  'Hyderabad': { lat: 17.385, lng: 78.4867 },
  'Pune': { lat: 18.5204, lng: 73.8567 },
  'Ahmedabad': { lat: 23.0225, lng: 72.5714 },
  'Jaipur': { lat: 26.9124, lng: 75.7873 },
  'Chandigarh': { lat: 30.7333, lng: 76.7794 },
  'Bhubaneswar': { lat: 20.2961, lng: 85.8245 },
};

export const useStore = create<StoreState>((set, get) => ({
  // Initial data
  vehicles: [],
  missions: [],
  alerts: [],
  agentLogs: [
    {
      id: 'log-init',
      time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      type: 'info',
      message: 'System initialized - Ready for operations',
    },
  ],
  driverEarnings: 0,
  fleetRevenue: 0,
  cities: [],

  // Current state
  currentMissionPlan: null,
  currentMissionId: null,
  currentDecision: null,
  ltlMatches: [],
  backhaulOptions: [],
  capacityInfo: null,

  // Loading states
  loading: false,
  error: null,

  // Setters
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  // ==========================================
  // FETCH DATA
  // ==========================================

  fetchRoutes: async () => {
    try {
      const result = await api.getRoutes();
      set({ cities: result.cities });
    } catch (error) {
      console.error('Failed to fetch routes:', error);
    }
  },

  fetchVehicles: async () => {
    try {
      const result = await api.getVehicles();
      const vehicles: Vehicle[] = result.vehicles.map((v) => {
        const coords = CITY_COORDS[v.current_city] || { lat: 20.5937, lng: 78.9629 };
        return {
          id: v.id,
          registration: v.registration,
          driverName: v.driver_name,
          vehicleNumber: v.registration,
          lat: coords.lat + (Math.random() - 0.5) * 0.1,
          lng: coords.lng + (Math.random() - 0.5) * 0.1,
          status: v.status as any,
          capacity_tons: v.capacity_tons,
          current_load_tons: v.current_load_tons,
        };
      });
      set({ vehicles });
    } catch (error) {
      console.error('Failed to fetch vehicles:', error);
    }
  },

  fetchMissions: async () => {
    try {
      const result = await api.listMissions();
      const missions: Mission[] = result.missions.map((m) => ({
        id: m.id,
        vehicleId: undefined,
        origin: m.origin,
        destination: m.destination,
        status: m.status as any,
        progress: m.progress_percent,
        eta: m.created_at,
        cargo: `${m.cargo.type} - ${m.cargo.weight_tons * 1000}kg`,
        cargoType: m.cargo.type,
        weightTons: m.cargo.weight_tons,
        distance: m.route?.distance_km || 0,
        revenue: m.route?.fare?.total_fare || 0,
        riskLevel: 'medium',
        currentLocation: m.current_location,
      }));
      set({ missions });
    } catch (error) {
      console.error('Failed to fetch missions:', error);
    }
  },

  // ==========================================
  // MODULE 1: MISSION PLANNER
  // ==========================================

  planNewMission: async (origin, destination, cargoType, weightTons) => {
    set({ loading: true, error: null });
    try {
      const result = await api.planMission({
        origin,
        destination,
        cargo_type: cargoType,
        weight_tons: weightTons,
      });

      const plan = result.plan;
      set({ currentMissionPlan: plan, loading: false });

      // Add agent log
      get().addAgentLog({
        id: `log-${Date.now()}`,
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        type: 'success',
        message: `Mission planned: ${origin} → ${destination} | Fare: ₹${plan.fare.calculated.total_fare.toLocaleString()}`,
      });

      return plan;
    } catch (error: any) {
      set({ error: error.message, loading: false });
      return null;
    }
  },

  startMission: async (vehicleId) => {
    const { currentMissionPlan } = get();
    if (!currentMissionPlan) return false;

    set({ loading: true });
    try {
      // For demo, we create a new mission directly
      const result = await api.getDemoScenario();
      set({
        currentMissionId: result.scenario.mission.id,
        loading: false
      });

      get().addAgentLog({
        id: `log-${Date.now()}`,
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        type: 'success',
        message: `Mission started with vehicle ${vehicleId}`,
      });

      return true;
    } catch (error: any) {
      set({ error: error.message, loading: false });
      return false;
    }
  },

  // ==========================================
  // MODULE 2: DECISION ENGINE
  // ==========================================

  evaluateSituation: async (missionId, location) => {
    set({ loading: true, error: null });
    try {
      const result = await api.evaluateSituation({
        mission_id: missionId,
        current_location: location,
      });

      const evaluation = result.evaluation;
      set({ currentDecision: evaluation, loading: false });

      // Add agent log
      get().addAgentLog({
        id: `log-${Date.now()}`,
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        type: evaluation.decision.action === 'CONTINUE' ? 'success' : 'warning',
        message: `Decision: ${evaluation.decision.action} - ${evaluation.ai_analysis.situation_assessment.substring(0, 50)}...`,
      });

      // Check for opportunities
      if (evaluation.decision.opportunities_found > 0) {
        get().addAlert({
          id: `alert-${Date.now()}`,
          type: 'opportunity',
          title: 'Opportunity Detected!',
          message: `${evaluation.decision.opportunities_found} load(s) available near ${location}`,
          timestamp: new Date(),
          data: evaluation.observation.nearby_opportunities,
        });
      }

      return evaluation;
    } catch (error: any) {
      set({ error: error.message, loading: false });
      return null;
    }
  },

  evaluateOpportunity: async (missionId, opportunity) => {
    set({ loading: true });
    try {
      const result = await api.evaluateOpportunity(missionId, opportunity);
      set({ loading: false });

      get().addAgentLog({
        id: `log-${Date.now()}`,
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        type: 'info',
        message: `Opportunity evaluated: ${result.evaluation.final_recommendation.recommendation}`,
      });

      return result.evaluation;
    } catch (error: any) {
      set({ error: error.message, loading: false });
      return null;
    }
  },

  // ==========================================
  // MODULE 3: CAPACITY MANAGER
  // ==========================================

  findLTLMatches: async (missionId) => {
    set({ loading: true, error: null });
    try {
      const result = await api.findLTLMatches(missionId);
      const matches = result.ltl_matches;

      set({
        ltlMatches: matches.available_loads || [],
        capacityInfo: matches.capacity,
        loading: false,
      });

      get().addAgentLog({
        id: `log-${Date.now()}`,
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        type: 'info',
        message: `Found ${matches.summary.loads_found} LTL loads - Potential revenue: ₹${matches.summary.total_potential_revenue.toLocaleString()}`,
      });
    } catch (error: any) {
      set({ error: error.message, loading: false });
    }
  },

  findBackhaul: async (missionId, homeBase) => {
    set({ loading: true, error: null });
    try {
      const result = await api.findBackhaul(missionId, homeBase);
      const backhaul = result.backhaul_options;

      set({
        backhaulOptions: backhaul.backhaul_options || [],
        loading: false,
      });

      get().addAgentLog({
        id: `log-${Date.now()}`,
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        type: 'info',
        message: `Empty return cost: ₹${backhaul.empty_return_cost.total.toLocaleString()} | Found ${backhaul.backhaul_options?.length || 0} backhaul options`,
      });
    } catch (error: any) {
      set({ error: error.message, loading: false });
    }
  },

  acceptLTLLoad: async (missionId, loadId) => {
    set({ loading: true });
    try {
      await api.acceptLTLLoad(missionId, loadId);
      set({ loading: false });

      get().addAgentLog({
        id: `log-${Date.now()}`,
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        type: 'success',
        message: `LTL load ${loadId} accepted - Capacity utilization increased`,
      });

      return true;
    } catch (error: any) {
      set({ error: error.message, loading: false });
      return false;
    }
  },

  bookBackhaul: async (missionId, loadId) => {
    set({ loading: true });
    try {
      await api.bookBackhaul(missionId, loadId);
      set({ loading: false });

      get().addAgentLog({
        id: `log-${Date.now()}`,
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        type: 'success',
        message: `Backhaul ${loadId} booked - Zero dead miles on return!`,
      });

      return true;
    } catch (error: any) {
      set({ error: error.message, loading: false });
      return false;
    }
  },

  getCapacityOverview: async () => {
    try {
      const result = await api.getCapacityOverview();
      return result.overview;
    } catch (error) {
      console.error('Failed to get capacity overview:', error);
      return null;
    }
  },

  // ==========================================
  // DEMO
  // ==========================================

  loadDemoScenario: async () => {
    set({ loading: true });
    try {
      const result = await api.getDemoScenario();
      const scenario = result.scenario;

      // Set the demo mission
      set({
        currentMissionId: scenario.mission.id,
        missions: [{
          id: scenario.mission.id,
          origin: scenario.mission.origin,
          destination: scenario.mission.destination,
          status: scenario.mission.status as any,
          progress: scenario.mission.progress_percent,
          eta: scenario.mission.created_at,
          cargo: `${scenario.mission.cargo?.type} - ${(scenario.mission.cargo?.weight_tons || 0) * 1000}kg`,
          cargoType: scenario.mission.cargo?.type || '',
          weightTons: scenario.mission.cargo?.weight_tons || 0,
          distance: scenario.mission.route?.distance_km || 0,
          revenue: scenario.mission.fare?.calculated?.total_fare || 0,
          riskLevel: scenario.mission.risk_assessment?.level || 'medium',
          currentLocation: scenario.mission.current_location,
        }],
        loading: false,
      });

      get().addAgentLog({
        id: `log-${Date.now()}`,
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        type: 'success',
        message: `Demo loaded: ${scenario.name}`,
      });

      // Fetch vehicles too
      await get().fetchVehicles();

    } catch (error: any) {
      set({ error: error.message, loading: false });
    }
  },

  resetDemo: async () => {
    set({ loading: true });
    try {
      await api.resetDemoData();
      set({
        missions: [],
        currentMissionPlan: null,
        currentMissionId: null,
        currentDecision: null,
        ltlMatches: [],
        backhaulOptions: [],
        loading: false,
      });

      get().addAgentLog({
        id: `log-${Date.now()}`,
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        type: 'info',
        message: 'Demo data reset',
      });
    } catch (error: any) {
      set({ error: error.message, loading: false });
    }
  },

  // ==========================================
  // LOCAL ACTIONS
  // ==========================================

  updateVehiclePosition: (id, lat, lng) =>
    set((state) => ({
      vehicles: state.vehicles.map((v) =>
        v.id === id ? { ...v, lat, lng } : v
      ),
    })),

  addAlert: (alert) =>
    set((state) => ({
      alerts: [...state.alerts, alert],
    })),

  removeAlert: (id) =>
    set((state) => ({
      alerts: state.alerts.filter((a) => a.id !== id),
    })),

  addAgentLog: (log) =>
    set((state) => ({
      agentLogs: [log, ...state.agentLogs].slice(0, 20), // Keep last 20 logs
    })),
}));
