import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import { Truck, TrendingUp, Activity, DollarSign, AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import { useStore } from '../../store/useStore';
import { KPICard } from '../ui/KPICard';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

const createCustomIcon = (color: string) => {
  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="background-color: ${color}; width: 24px; height: 24px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.3);"></div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });
};

export function CommandCenter() {
  const {
    vehicles,
    missions,
    agentLogs,
    currentMissionId,
    loadDemoScenario,
    fetchVehicles,
    evaluateSituation,
    findLTLMatches,
    findBackhaul,
    currentDecision,
    ltlMatches,
    capacityInfo,
    loading,
    updateVehiclePosition
  } = useStore();

  const [activeVehicles, setActiveVehicles] = useState(0);
  const [utilization, setUtilization] = useState(0);
  const [showDecisionPanel, setShowDecisionPanel] = useState(false);

  useEffect(() => {
    loadDemoScenario();
  }, [loadDemoScenario]);

  useEffect(() => {
    const active = vehicles.filter((v) => v.status === 'moving' || v.status === 'in_transit').length;
    setActiveVehicles(active);
    setUtilization(vehicles.length > 0 ? Math.round((active / vehicles.length) * 100) : 0);
  }, [vehicles]);

  useEffect(() => {
    const interval = setInterval(() => {
      vehicles.forEach((vehicle) => {
        if (vehicle.status === 'moving' || vehicle.status === 'in_transit') {
          const newLat = vehicle.lat + (Math.random() - 0.5) * 0.02;
          const newLng = vehicle.lng + (Math.random() - 0.5) * 0.02;
          updateVehiclePosition(vehicle.id, newLat, newLng);
        }
      });
    }, 3000);

    return () => clearInterval(interval);
  }, [vehicles, updateVehiclePosition]);

  const getMarkerColor = (status: string) => {
    switch (status) {
      case 'moving':
      case 'in_transit':
        return '#10B981';
      case 'stopped':
        return '#EF4444';
      case 'idle':
      case 'available':
        return '#9CA3AF';
      default:
        return '#2563EB';
    }
  };

  const handleEvaluateSituation = async () => {
    if (currentMissionId) {
      await evaluateSituation(currentMissionId, 'Ahmedabad');
      setShowDecisionPanel(true);
    }
  };

  const handleFindLTL = async () => {
    if (currentMissionId) {
      await findLTLMatches(currentMissionId);
    }
  };

  const handleFindBackhaul = async () => {
    if (currentMissionId) {
      await findBackhaul(currentMissionId, 'Mumbai');
    }
  };

  const currentMission = missions.find(m => m.id === currentMissionId) || missions[0];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">Command Center</h1>
          <p className="text-gray-600">Real-time fleet monitoring and AI decision engine</p>
        </div>
        {currentMissionId && (
          <div className="flex gap-2">
            <Button onClick={handleEvaluateSituation} variant="primary" disabled={loading}>
              Evaluate Situation
            </Button>
            <Button onClick={handleFindLTL} variant="warning" disabled={loading}>
              Find LTL Loads
            </Button>
            <Button onClick={handleFindBackhaul} variant="success" disabled={loading}>
              Find Backhaul
            </Button>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <KPICard
          title="Active Missions"
          value={missions.filter((m) => m.status === 'active' || m.status === 'in_progress').length}
          icon={Activity}
          trend={{ value: '12%', positive: true }}
        />
        <KPICard
          title="Vehicles Online"
          value={activeVehicles}
          icon={Truck}
          color="text-neuro-blue"
        />
        <KPICard
          title="Fleet Utilization"
          value={`${capacityInfo?.utilization_percent || utilization}%`}
          icon={TrendingUp}
          color="text-signal-amber"
        />
        <KPICard
          title="Available Capacity"
          value={`${capacityInfo?.available_tons || 0}T`}
          icon={DollarSign}
          trend={{ value: 'Pooling ready', positive: true }}
          color="text-profit-green"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <h3 className="font-bold text-lg mb-4">Live Fleet Map</h3>
          <div className="h-96 rounded-lg overflow-hidden">
            <MapContainer
              center={[20.5937, 78.9629]}
              zoom={5}
              style={{ height: '100%', width: '100%' }}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              {vehicles.map((vehicle) => (
                <Marker
                  key={vehicle.id}
                  position={[vehicle.lat, vehicle.lng]}
                  icon={createCustomIcon(getMarkerColor(vehicle.status))}
                >
                  <Popup>
                    <div className="font-sans">
                      <p className="font-bold">{vehicle.driverName}</p>
                      <p className="text-sm text-gray-600">{vehicle.vehicleNumber}</p>
                      <p className="text-sm">
                        Status:{' '}
                        <span
                          className={`font-semibold ${vehicle.status === 'moving' || vehicle.status === 'in_transit'
                              ? 'text-profit-green'
                              : vehicle.status === 'stopped'
                                ? 'text-risk-red'
                                : 'text-gray-600'
                            }`}
                        >
                          {vehicle.status}
                        </span>
                      </p>
                      <p className="text-sm">
                        Capacity: {vehicle.current_load_tons}/{vehicle.capacity_tons}T
                      </p>
                    </div>
                  </Popup>
                </Marker>
              ))}
              {missions.map((mission) => {
                const vehicle = vehicles.find((v) => v.id === mission.vehicleId);
                if (!vehicle) return null;
                return (
                  <Polyline
                    key={mission.id}
                    positions={[
                      [vehicle.lat, vehicle.lng],
                      [vehicle.lat + 2, vehicle.lng + 2],
                    ]}
                    color="#2563EB"
                    weight={3}
                    opacity={0.6}
                    dashArray="10, 10"
                  />
                );
              })}
            </MapContainer>
          </div>
        </Card>

        <Card>
          <h3 className="font-bold text-lg mb-4">Active Mission</h3>
          {currentMission ? (
            <div className="space-y-4">
              <div className="p-4 bg-gradient-to-r from-neuro-blue to-blue-700 rounded-lg text-white">
                <p className="text-sm text-blue-200">Current Route</p>
                <p className="font-bold text-lg">{currentMission.origin} → {currentMission.destination}</p>
                <div className="mt-2 bg-white/20 rounded-full h-2">
                  <div
                    className="bg-signal-amber h-2 rounded-full transition-all"
                    style={{ width: `${currentMission.progress}%` }}
                  />
                </div>
                <p className="text-sm mt-1">{currentMission.progress}% Complete</p>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Cargo</span>
                  <span className="font-semibold">{currentMission.cargo}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Distance</span>
                  <span className="font-semibold">{currentMission.distance} km</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Risk Level</span>
                  <span className={`font-semibold ${currentMission.riskLevel === 'low' ? 'text-profit-green' :
                      currentMission.riskLevel === 'medium' ? 'text-signal-amber' :
                        'text-risk-red'
                    }`}>
                    {currentMission.riskLevel?.toUpperCase()}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Current Location</span>
                  <span className="font-semibold">{currentMission.currentLocation || 'En route'}</span>
                </div>
              </div>
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No active mission</p>
          )}
        </Card>
      </div>

      {/* Decision Panel */}
      {showDecisionPanel && currentDecision && (
        <Card className="border-2 border-signal-amber">
          <div className="flex items-center gap-3 mb-4">
            <div className={`p-2 rounded-full ${currentDecision.decision.action === 'CONTINUE' ? 'bg-profit-green/20' :
                currentDecision.decision.action === 'ALERT' ? 'bg-signal-amber/20' :
                  'bg-risk-red/20'
              }`}>
              {currentDecision.decision.action === 'CONTINUE' ? (
                <CheckCircle className="text-profit-green" size={24} />
              ) : currentDecision.decision.action === 'ALERT' ? (
                <AlertTriangle className="text-signal-amber" size={24} />
              ) : (
                <AlertTriangle className="text-risk-red" size={24} />
              )}
            </div>
            <div>
              <h3 className="font-bold text-lg">AI Decision: {currentDecision.decision.action}</h3>
              <p className="text-sm text-gray-600">Confidence: {(currentDecision.decision.confidence * 100).toFixed(0)}%</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <h4 className="font-semibold mb-2">Current Conditions</h4>
              <div className="space-y-1 text-sm">
                <p>Traffic: <span className={
                  currentDecision.observation.conditions.traffic === 'clear' ? 'text-profit-green' :
                    currentDecision.observation.conditions.traffic === 'moderate' ? 'text-signal-amber' :
                      'text-risk-red'
                }>{currentDecision.observation.conditions.traffic}</span></p>
                <p>Weather: <span className={
                  currentDecision.observation.conditions.weather === 'clear' ? 'text-profit-green' :
                    'text-signal-amber'
                }>{currentDecision.observation.conditions.weather}</span></p>
                <p>Fuel: {currentDecision.observation.conditions.fuel_level_percent}%</p>
                <p>Driver Fatigue: {currentDecision.observation.conditions.driver_fatigue_level}</p>
              </div>
            </div>

            <div className="p-4 bg-gray-50 rounded-lg">
              <h4 className="font-semibold mb-2">AI Assessment</h4>
              <p className="text-sm text-gray-700">{currentDecision.ai_analysis.situation_assessment}</p>
            </div>
          </div>

          {currentDecision.decision.opportunities_found > 0 && (
            <div className="p-4 bg-profit-green/10 rounded-lg border border-profit-green">
              <p className="font-semibold text-profit-green">
                💰 {currentDecision.decision.opportunities_found} revenue opportunity(ies) detected nearby!
              </p>
            </div>
          )}

          <Button
            onClick={() => setShowDecisionPanel(false)}
            variant="primary"
            className="mt-4"
          >
            Acknowledge
          </Button>
        </Card>
      )}

      {/* LTL Matches Panel */}
      {ltlMatches.length > 0 && (
        <Card>
          <h3 className="font-bold text-lg mb-4">Available LTL Loads (Module 3: Capacity Manager)</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {ltlMatches.map((load: any) => (
              <div key={load.id} className="p-4 bg-gray-50 rounded-lg border hover:border-profit-green transition-colors">
                <p className="font-semibold">{load.cargo_type}</p>
                <p className="text-sm text-gray-600">{load.pickup_city} → {load.delivery_city}</p>
                <div className="flex justify-between mt-2">
                  <span className="text-sm text-gray-500">{load.weight_tons}T</span>
                  <span className="font-bold text-profit-green">₹{load.offered_rate?.toLocaleString()}</span>
                </div>
                <Button variant="success" size="sm" className="w-full mt-2">
                  Accept Load
                </Button>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* AI Agent Activity Log */}
      <Card className="bg-neuro-slate text-white">
        <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
          <span className="w-2 h-2 bg-profit-green rounded-full animate-pulse" />
          AI Agent Activity Log
        </h3>
        <div className="space-y-3 max-h-64 overflow-y-auto">
          {agentLogs.map((log) => (
            <div key={log.id} className="flex items-start gap-3 text-sm">
              <span className="text-blue-400 font-mono min-w-[60px]">{log.time}</span>
              <span className="text-gray-400">•</span>
              <span className={
                log.type === 'warning' ? 'text-signal-amber' :
                  log.type === 'success' ? 'text-profit-green' :
                    log.type === 'decision' ? 'text-neuro-blue' :
                      ''
              }>
                {log.message}
              </span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
