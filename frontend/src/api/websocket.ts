import { io, Socket } from 'socket.io-client';
import { WS_BASE_URL, WS_EVENTS, STORAGE_KEYS } from '../utils/constants';
import type { VehicleLocationUpdate, RouteDeviationAlert, Notification } from '../types';

// ==========================================
// WEBSOCKET CLASS
// ==========================================

class WebSocketService {
    private socket: Socket | null = null;
    private reconnectAttempts = 0;
    private maxReconnectAttempts = 5;

    constructor() {
        this.socket = null;
    }

    connect(): void {
        console.log("🔌 MOCK MODE: WebSocket simulation active");
        // No real connection in mock mode
    }

    disconnect(): void {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }
    }

    isConnected(): boolean {
        return this.socket?.connected || false;
    }

    // ==========================================
    // VEHICLE LOCATION UPDATES
    // ==========================================

    onVehicleLocationUpdate(callback: (data: VehicleLocationUpdate) => void): void {
        if (!this.socket) return;
        this.socket.on(WS_EVENTS.VEHICLE_LOCATION_UPDATE, callback);
    }

    offVehicleLocationUpdate(callback: (data: VehicleLocationUpdate) => void): void {
        if (!this.socket) return;
        this.socket.off(WS_EVENTS.VEHICLE_LOCATION_UPDATE, callback);
    }

    // ==========================================
    // ROUTE DEVIATION ALERTS
    // ==========================================

    onRouteDeviation(callback: (data: RouteDeviationAlert) => void): void {
        if (!this.socket) return;
        this.socket.on(WS_EVENTS.ROUTE_DEVIATION, callback);
    }

    offRouteDeviation(callback: (data: RouteDeviationAlert) => void): void {
        if (!this.socket) return;
        this.socket.off(WS_EVENTS.ROUTE_DEVIATION, callback);
    }

    // ==========================================
    // LOAD STATUS CHANGES
    // ==========================================

    onLoadStatusChange(callback: (data: any) => void): void {
        if (!this.socket) return;
        this.socket.on(WS_EVENTS.LOAD_STATUS_CHANGE, callback);
    }

    offLoadStatusChange(callback: (data: any) => void): void {
        if (!this.socket) return;
        this.socket.off(WS_EVENTS.LOAD_STATUS_CHANGE, callback);
    }

    // ==========================================
    // NOTIFICATIONS
    // ==========================================

    onNotification(callback: (data: Notification) => void): void {
        if (!this.socket) return;
        this.socket.on(WS_EVENTS.NOTIFICATION, callback);
    }

    offNotification(callback: (data: Notification) => void): void {
        if (!this.socket) return;
        this.socket.off(WS_EVENTS.NOTIFICATION, callback);
    }

    // ==========================================
    // CUSTOM EVENTS
    // ==========================================

    on(event: string, callback: (...args: any[]) => void): void {
        if (!this.socket) return;
        this.socket.on(event, callback);
    }

    off(event: string, callback: (...args: any[]) => void): void {
        if (!this.socket) return;
        this.socket.off(event, callback);
    }

    emit(event: string, data: any): void {
        if (!this.socket) return;
        this.socket.emit(event, data);
    }
}

// ==========================================
// SINGLETON INSTANCE
// ==========================================

const websocketService = new WebSocketService();
export default websocketService;
