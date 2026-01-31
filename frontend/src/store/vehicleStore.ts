import { create } from 'zustand';
import { Vehicle, Coordinates } from '../types';
import { vehicleApi } from '../api';

// ==========================================
// VEHICLE STORE STATE
// ==========================================

interface VehicleState {
    vehicles: Vehicle[];
    selectedVehicle: Vehicle | null;
    isLoading: boolean;
    error: string | null;
}

interface VehicleActions {
    fetchVehicles: () => Promise<void>;
    fetchVehicleById: (id: string) => Promise<void>;
    selectVehicle: (vehicle: Vehicle | null) => void;
    updateVehicleLocation: (id: string, location: Coordinates) => void;
    updateVehicleStatus: (id: string, status: string) => Promise<void>;
    clearError: () => void;
}

type VehicleStore = VehicleState & VehicleActions;

// ==========================================
// ZUSTAND STORE
// ==========================================

export const useVehicleStore = create<VehicleStore>((set, get) => ({
    // Initial State
    vehicles: [],
    selectedVehicle: null,
    isLoading: false,
    error: null,

    // Actions
    fetchVehicles: async () => {
        set({ isLoading: true, error: null });

        try {
            const vehicles = await vehicleApi.getAll();
            set({ vehicles, isLoading: false });
        } catch (error: any) {
            set({
                error: error.response?.data?.message || 'Failed to fetch vehicles',
                isLoading: false,
            });
        }
    },

    fetchVehicleById: async (id: string) => {
        set({ isLoading: true, error: null });

        try {
            const vehicle = await vehicleApi.getById(id);
            set({ selectedVehicle: vehicle, isLoading: false });
        } catch (error: any) {
            set({
                error: error.response?.data?.message || 'Failed to fetch vehicle',
                isLoading: false,
            });
        }
    },

    selectVehicle: (vehicle) => {
        set({ selectedVehicle: vehicle });
    },

    updateVehicleLocation: (id, location) => {
        set((state) => ({
            vehicles: state.vehicles.map((v) =>
                v.id === id
                    ? { ...v, currentLocation: location, lastUpdated: new Date().toISOString() }
                    : v
            ),
            selectedVehicle:
                state.selectedVehicle?.id === id
                    ? { ...state.selectedVehicle, currentLocation: location, lastUpdated: new Date().toISOString() }
                    : state.selectedVehicle,
        }));
    },

    updateVehicleStatus: async (id, status) => {
        try {
            await vehicleApi.updateStatus(id, status);

            set((state) => ({
                vehicles: state.vehicles.map((v) =>
                    v.id === id ? { ...v, status: status as any } : v
                ),
                selectedVehicle:
                    state.selectedVehicle?.id === id
                        ? { ...state.selectedVehicle, status: status as any }
                        : state.selectedVehicle,
            }));
        } catch (error: any) {
            set({
                error: error.response?.data?.message || 'Failed to update vehicle status',
            });
        }
    },

    clearError: () => {
        set({ error: null });
    },
}));
