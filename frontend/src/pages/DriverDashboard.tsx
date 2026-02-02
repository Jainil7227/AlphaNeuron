import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Menu, Bell, Navigation, DollarSign, MapPin, Clock, X,
  TrendingUp, AlertTriangle, Brain, Home, Settings,
  HelpCircle, LogOut, ChevronRight, Mic,
  Fuel, CloudRain, Car, Zap
} from 'lucide-react';
import { MapContainer, TileLayer, Marker, Polyline, Popup } from 'react-leaflet';
import { useStore } from '../store/useStore';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { copilotChat } from '../services/api';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Custom marker icon
const createIcon = (color: string) => L.divIcon({
  className: 'custom-marker',
  html: `<div style="background-color: ${color}; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.3);"></div>`,
  iconSize: [20, 20],
  iconAnchor: [10, 10],
});

// Route coordinates for demo
const ROUTE_COORDS = {
  'Mumbai': { lat: 19.076, lng: 72.8777 },
  'Ahmedabad': { lat: 23.0225, lng: 72.5714 },
  'Jaipur': { lat: 26.9124, lng: 75.7873 },
  'Delhi': { lat: 28.7041, lng: 77.1025 },
};

export function DriverDashboard() {
  const {
    missions,
    alerts,
    agentLogs,
    currentMissionId,
    loading,
    loadDemoScenario,
    evaluateSituation,
    currentDecision,
    removeAlert,
    addAgentLog,
  } = useStore();

  const [showSideMenu, setShowSideMenu] = useState(false);
  const [showAlert, setShowAlert] = useState(false);
  const [showNavigation, setShowNavigation] = useState(false);
  const [showCopilot, setShowCopilot] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showHelp, setShowHelp] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [earnings, setEarnings] = useState(8450);
  const [copilotMessages, setCopilotMessages] = useState<Array<{ id: string; type: 'agent' | 'user'; message: string; time: string }>>([]);
  const [currentPosition, setCurrentPosition] = useState(0.35); // 35% along route
  const copilotEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadDemoScenario();
  }, [loadDemoScenario]);

  // Auto-scroll copilot messages
  useEffect(() => {
    copilotEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [copilotMessages]);

  // Simulate vehicle movement along route
  useEffect(() => {
    if (showNavigation) {
      const interval = setInterval(() => {
        setCurrentPosition(prev => {
          if (prev >= 1) return 0.35;
          return prev + 0.005;
        });
      }, 500);
      return () => clearInterval(interval);
    }
  }, [showNavigation]);

  // Simulate opportunty alert after 5 seconds
  useEffect(() => {
    const timer = setTimeout(() => {
      const opportunityAlert = {
        id: `opp-${Date.now()}`,
        type: 'opportunity' as const,
        title: 'New Load Match Detected!',
        message: 'Additional cargo matches your route - AI recommends accepting',
        pickup: '5km away',
        extraPay: 2500,
        detour: '+15 mins',
        timestamp: new Date(),
      };
      useStore.getState().addAlert(opportunityAlert);
      setShowAlert(true);
    }, 8000);

    return () => clearTimeout(timer);
  }, []);

  const currentMission = missions.find(m => m.id === currentMissionId) || missions[0];

  // Calculate current position on route
  const getInterpolatedPosition = () => {
    const routePoints = [
      ROUTE_COORDS['Mumbai'],
      ROUTE_COORDS['Ahmedabad'],
      ROUTE_COORDS['Jaipur'],
      ROUTE_COORDS['Delhi'],
    ];

    const totalSegments = routePoints.length - 1;
    const segmentIndex = Math.min(Math.floor(currentPosition * totalSegments), totalSegments - 1);
    const segmentProgress = (currentPosition * totalSegments) - segmentIndex;

    const start = routePoints[segmentIndex];
    const end = routePoints[segmentIndex + 1];

    return {
      lat: start.lat + (end.lat - start.lat) * segmentProgress,
      lng: start.lng + (end.lng - start.lng) * segmentProgress,
    };
  };

  const handleAcceptOpportunity = () => {
    setShowAlert(false);
    if (alerts.length > 0) {
      removeAlert(alerts[0].id);
      setEarnings(prev => prev + (alerts[0].extraPay || 2500));
      addAgentLog({
        id: `log-${Date.now()}`,
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        type: 'success',
        message: 'Driver accepted LTL opportunity - Revenue increased!',
      });

      // Add copilot message
      addCopilotMessage('agent', 'Great choice! I\'ve added the pickup to your route. You\'ll earn an extra ₹2,500 with just 15 minutes detour. 💰');
    }
  };

  const handleRejectOpportunity = () => {
    setShowAlert(false);
    if (alerts.length > 0) {
      removeAlert(alerts[0].id);
      addAgentLog({
        id: `log-${Date.now()}`,
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        type: 'info',
        message: 'Driver rejected LTL opportunity',
      });
    }
  };

  const addCopilotMessage = (type: 'agent' | 'user', message: string) => {
    setCopilotMessages(prev => [...prev, {
      id: `msg-${Date.now()}`,
      type,
      message,
      time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    }]);
  };

  const handleAICheck = async () => {
    setShowCopilot(true);

    // Add initial copilot message
    addCopilotMessage('agent', 'Starting AI situation analysis... 🔍');

    if (currentMissionId) {
      const result = await evaluateSituation(currentMissionId, 'Ahmedabad');

      if (result) {
        // Add analysis messages
        setTimeout(() => {
          addCopilotMessage('agent', `📍 Current Status: ${Math.round(currentPosition * 100)}% complete, approaching Ahmedabad`);
        }, 500);

        setTimeout(() => {
          const traffic = result.observation?.conditions?.traffic || 'moderate';
          const weather = result.observation?.conditions?.weather || 'clear';
          addCopilotMessage('agent', `🚦 Traffic: ${traffic.toUpperCase()} | ☁️ Weather: ${weather}`);
        }, 1000);

        setTimeout(() => {
          addCopilotMessage('agent', `⚡ AI Decision: ${result.decision?.action || 'CONTINUE'} - ${result.ai_analysis?.situation_assessment?.substring(0, 100) || 'Route is clear, continue as planned'}...`);
        }, 1500);

        if (result.decision?.opportunities_found > 0) {
          setTimeout(() => {
            addCopilotMessage('agent', `💰 Opportunity Alert: ${result.decision.opportunities_found} revenue opportunity detected nearby!`);
          }, 2000);
        }

        setTimeout(() => {
          addCopilotMessage('agent', '✅ Analysis complete. I\'ll keep monitoring and alert you to any changes.');
        }, 2500);
      }
    }
  };

  const handleNavigate = () => {
    setShowNavigation(true);
    addCopilotMessage('agent', '🗺️ Navigation started! Taking you via NH48 Mumbai-Delhi Highway. ETA: 27.6 hours.');

    // Simulate route updates
    setTimeout(() => {
      addCopilotMessage('agent', '📍 First checkpoint: Ahmedabad (530 km). Fuel stop recommended at Vadodara.');
    }, 3000);
  };

  const routePolyline = [
    [ROUTE_COORDS['Mumbai'].lat, ROUTE_COORDS['Mumbai'].lng],
    [ROUTE_COORDS['Ahmedabad'].lat, ROUTE_COORDS['Ahmedabad'].lng],
    [ROUTE_COORDS['Jaipur'].lat, ROUTE_COORDS['Jaipur'].lng],
    [ROUTE_COORDS['Delhi'].lat, ROUTE_COORDS['Delhi'].lng],
  ] as [number, number][];

  const currentPos = getInterpolatedPosition();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Side Menu Overlay */}
      <AnimatePresence>
        {showSideMenu && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 z-40"
              onClick={() => setShowSideMenu(false)}
            />
            <motion.div
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ type: 'spring', damping: 25 }}
              className="fixed left-0 top-0 bottom-0 w-72 bg-neuro-slate text-white z-50 shadow-2xl"
            >
              <div className="p-6">
                <div className="flex items-center gap-4 mb-8">
                  <div className="w-14 h-14 bg-gradient-to-br from-signal-amber to-orange-500 rounded-full flex items-center justify-center text-2xl font-bold">
                    R
                  </div>
                  <div>
                    <h3 className="font-bold text-lg">Rajesh Kumar</h3>
                    <p className="text-sm text-blue-300">Driver ID: DRV-001</p>
                  </div>
                </div>

                <nav className="space-y-2">
                  <button
                    onClick={() => setShowSideMenu(false)}
                    className="w-full flex items-center gap-3 px-4 py-3 rounded-lg bg-neuro-blue text-white"
                  >
                    <Home size={20} />
                    <span>Dashboard</span>
                    <ChevronRight size={18} className="ml-auto" />
                  </button>
                  <button
                    onClick={() => { setShowCopilot(true); setShowSideMenu(false); }}
                    className="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-white/10 transition-colors"
                  >
                    <Brain size={20} className="text-signal-amber" />
                    <span>AI Copilot</span>
                    <span className="ml-auto px-2 py-0.5 bg-signal-amber text-xs rounded-full">NEW</span>
                  </button>
                  <button
                    onClick={() => { setShowSettings(true); setShowSideMenu(false); }}
                    className="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-white/10 transition-colors"
                  >
                    <Settings size={20} />
                    <span>Settings</span>
                    <ChevronRight size={18} className="ml-auto" />
                  </button>
                  <button
                    onClick={() => { setShowHelp(true); setShowSideMenu(false); }}
                    className="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-white/10 transition-colors"
                  >
                    <HelpCircle size={20} />
                    <span>Help & Support</span>
                    <ChevronRight size={18} className="ml-auto" />
                  </button>
                </nav>

                <div className="absolute bottom-6 left-6 right-6">
                  <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-red-400 hover:bg-red-500/10 transition-colors">
                    <LogOut size={20} />
                    <span>Logout</span>
                  </button>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Header */}
      <div className="bg-neuro-slate text-white p-4 flex items-center justify-between">
        <button onClick={() => setShowSideMenu(true)}>
          <Menu size={24} />
        </button>
        <div className="flex items-center gap-2">
          <Brain className="text-signal-amber" size={20} />
          <h1 className="text-lg font-bold">Neuro-Logistics</h1>
        </div>
        <button
          onClick={() => setShowNotifications(true)}
          className="relative p-2 hover:bg-white/10 rounded-full transition-colors"
        >
          <Bell size={24} />
          {alerts.length > 0 && (
            <span className="absolute top-0 right-0 bg-signal-amber text-xs rounded-full w-5 h-5 flex items-center justify-center">
              {alerts.length}
            </span>
          )}
        </button>
      </div>

      {/* Navigation Map View */}
      {showNavigation ? (
        <div className="relative h-[60vh]">
          <MapContainer
            center={[23.0225, 75.5]}
            zoom={6}
            style={{ height: '100%', width: '100%' }}
            zoomControl={false}
          >
            <TileLayer
              attribution='&copy; OpenStreetMap'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {/* Route line */}
            <Polyline
              positions={routePolyline}
              color="#2563EB"
              weight={5}
              opacity={0.8}
            />

            {/* Completed portion */}
            <Polyline
              positions={routePolyline.slice(0, Math.ceil(currentPosition * 4) + 1)}
              color="#10B981"
              weight={6}
              opacity={1}
            />

            {/* Origin marker */}
            <Marker
              position={[ROUTE_COORDS['Mumbai'].lat, ROUTE_COORDS['Mumbai'].lng]}
              icon={createIcon('#10B981')}
            >
              <Popup>Mumbai (Origin)</Popup>
            </Marker>

            {/* Destination marker */}
            <Marker
              position={[ROUTE_COORDS['Delhi'].lat, ROUTE_COORDS['Delhi'].lng]}
              icon={createIcon('#EF4444')}
            >
              <Popup>Delhi (Destination)</Popup>
            </Marker>

            {/* Current position */}
            <Marker
              position={[currentPos.lat, currentPos.lng]}
              icon={createIcon('#F59E0B')}
            >
              <Popup>You are here</Popup>
            </Marker>
          </MapContainer>

          {/* Navigation overlay */}
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-white to-transparent pt-8 pb-4 px-4">
            <Card className="bg-neuro-slate text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-blue-300">Next Stop</p>
                  <p className="font-bold text-lg">Ahmedabad</p>
                  <p className="text-sm">195 km • ~3h 20m</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-blue-300">ETA Delhi</p>
                  <p className="font-bold text-lg text-signal-amber">27.6h</p>
                  <p className="text-sm">{Math.round(currentPosition * 100)}% complete</p>
                </div>
              </div>
              <div className="mt-3 bg-white/20 rounded-full h-2">
                <div
                  className="bg-signal-amber h-2 rounded-full transition-all"
                  style={{ width: `${currentPosition * 100}%` }}
                />
              </div>
            </Card>
          </div>

          {/* Close navigation button */}
          <button
            onClick={() => setShowNavigation(false)}
            className="absolute top-4 right-4 bg-white hover:bg-gray-100 rounded-full p-3 shadow-xl z-50 transition-all"
          >
            <X size={28} className="text-neuro-slate" />
          </button>
        </div>
      ) : (
        <div className="p-4 space-y-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <h2 className="text-2xl font-bold mb-4">Good Morning, Rajesh!</h2>
          </motion.div>

          {/* Active Mission Card */}
          {currentMission && (
            <Card className="bg-gradient-to-br from-neuro-blue to-blue-700 text-white">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <p className="text-blue-200 text-sm mb-1">Active Mission</p>
                  <h3 className="text-xl font-bold">{currentMission.origin} → {currentMission.destination}</h3>
                </div>
                <Car className="text-blue-200" size={32} />
              </div>

              <div className="space-y-2 mb-4">
                <div className="flex items-center gap-2 text-sm">
                  <MapPin size={16} />
                  <span>{currentMission.cargo}</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Clock size={16} />
                  <span>Distance: {currentMission.distance} km</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <AlertTriangle size={16} className={
                    currentMission.riskLevel === 'low' ? 'text-profit-green' :
                      currentMission.riskLevel === 'medium' ? 'text-signal-amber' :
                        'text-risk-red'
                  } />
                  <span>Risk: {currentMission.riskLevel?.toUpperCase()}</span>
                </div>
              </div>

              <div className="bg-white/20 rounded-full h-2 mb-4">
                <div
                  className="bg-signal-amber h-2 rounded-full transition-all"
                  style={{ width: `${currentMission.progress}%` }}
                />
              </div>
              <p className="text-sm text-center mb-4">{currentMission.progress}% Complete</p>

              <div className="grid grid-cols-2 gap-2">
                <Button
                  variant="warning"
                  className="flex items-center justify-center gap-2"
                  onClick={handleNavigate}
                >
                  <Navigation size={18} />
                  Navigate
                </Button>
                <Button
                  variant="primary"
                  className="flex items-center justify-center gap-2 bg-white/20"
                  onClick={handleAICheck}
                  disabled={loading}
                >
                  <Brain size={18} />
                  AI Check
                </Button>
              </div>
            </Card>
          )}

          {/* KPI Cards */}
          <div className="grid grid-cols-2 gap-4">
            <Card>
              <div className="flex items-center gap-3">
                <div className="p-3 bg-profit-green/10 rounded-lg">
                  <DollarSign className="text-profit-green" size={24} />
                </div>
                <div>
                  <p className="text-xs text-gray-600">Today's Earnings</p>
                  <p className="text-xl font-bold font-mono">₹{earnings.toLocaleString()}</p>
                </div>
              </div>
            </Card>

            <Card>
              <div className="flex items-center gap-3">
                <div className="p-3 bg-neuro-blue/10 rounded-lg">
                  <MapPin className="text-neuro-blue" size={24} />
                </div>
                <div>
                  <p className="text-xs text-gray-600">Distance</p>
                  <p className="text-xl font-bold font-mono">{currentMission?.distance || 0} km</p>
                </div>
              </div>
            </Card>
          </div>

          {/* Capacity Indicator */}
          <Card>
            <h3 className="font-bold mb-3 flex items-center gap-2">
              <TrendingUp className="text-signal-amber" size={18} />
              Truck Capacity
            </h3>
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <div className="bg-gray-200 rounded-full h-4">
                  <div
                    className="bg-gradient-to-r from-signal-amber to-profit-green h-4 rounded-full transition-all"
                    style={{ width: '48%' }}
                  />
                </div>
              </div>
              <span className="font-mono font-bold">48%</span>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              💡 13 tons available - AI may suggest LTL loads to maximize earnings
            </p>
          </Card>

          {/* Agent Activity Feed */}
          <Card className="bg-neuro-slate text-white">
            <h3 className="font-bold mb-3 flex items-center gap-2">
              <span className="w-2 h-2 bg-profit-green rounded-full animate-pulse" />
              AI Agent Activity
            </h3>
            <div className="space-y-2 max-h-32 overflow-y-auto">
              {agentLogs.slice(0, 5).map((log) => (
                <div key={log.id} className="text-sm flex items-center gap-2">
                  <span className="text-blue-400">{log.time}</span>
                  <span className="text-gray-400">•</span>
                  <span className={
                    log.type === 'warning' ? 'text-signal-amber' :
                      log.type === 'success' ? 'text-profit-green' :
                        ''
                  }>
                    {log.message.length > 40 ? log.message.substring(0, 40) + '...' : log.message}
                  </span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {/* AI Copilot Panel - Full Screen */}
      <AnimatePresence>
        {showCopilot && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-white z-50 flex flex-col"
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-neuro-blue to-blue-700 text-white p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-white/20 rounded-full">
                  <Brain size={24} className="text-signal-amber" />
                </div>
                <div>
                  <h3 className="font-bold">AI Copilot</h3>
                  <p className="text-xs text-blue-200">Real-time route intelligence</p>
                </div>
              </div>
              <button
                onClick={() => setShowCopilot(false)}
                className="p-2 hover:bg-white/20 rounded-full transition-colors"
              >
                <X size={24} />
              </button>
            </div>

            {/* Map Section - Top Half */}
            <div className="h-[35vh] relative">
              <MapContainer
                center={[23.5, 76]}
                zoom={5}
                style={{ height: '100%', width: '100%' }}
                zoomControl={false}
              >
                <TileLayer
                  attribution='&copy; OSM'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                {/* Route polyline - remaining */}
                <Polyline
                  positions={routePolyline}
                  color="#2563EB"
                  weight={4}
                  opacity={0.5}
                  dashArray="10, 10"
                />

                {/* Completed portion */}
                <Polyline
                  positions={routePolyline.slice(0, Math.ceil(currentPosition * 4) + 1)}
                  color="#10B981"
                  weight={6}
                  opacity={1}
                />

                {/* Start marker */}
                <Marker
                  position={[ROUTE_COORDS['Mumbai'].lat, ROUTE_COORDS['Mumbai'].lng]}
                  icon={createIcon('#10B981')}
                >
                  <Popup>🟢 Mumbai (Start)</Popup>
                </Marker>

                {/* Waypoints */}
                <Marker
                  position={[ROUTE_COORDS['Ahmedabad'].lat, ROUTE_COORDS['Ahmedabad'].lng]}
                  icon={createIcon('#6B7280')}
                >
                  <Popup>📍 Ahmedabad (Checkpoint)</Popup>
                </Marker>

                <Marker
                  position={[ROUTE_COORDS['Jaipur'].lat, ROUTE_COORDS['Jaipur'].lng]}
                  icon={createIcon('#6B7280')}
                >
                  <Popup>📍 Jaipur (Checkpoint)</Popup>
                </Marker>

                {/* End marker */}
                <Marker
                  position={[ROUTE_COORDS['Delhi'].lat, ROUTE_COORDS['Delhi'].lng]}
                  icon={createIcon('#EF4444')}
                >
                  <Popup>🔴 Delhi (Destination)</Popup>
                </Marker>

                {/* Current position - driver */}
                <Marker
                  position={[currentPos.lat, currentPos.lng]}
                  icon={createIcon('#F59E0B')}
                >
                  <Popup>🚛 You are here</Popup>
                </Marker>
              </MapContainer>

              {/* Route progress overlay */}
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-neuro-slate to-transparent p-4">
                <div className="flex items-center justify-between text-white text-sm mb-2">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-profit-green rounded-full animate-pulse"></div>
                    <span className="font-semibold">Mumbai</span>
                  </div>
                  <span className="px-3 py-1 bg-signal-amber rounded-full font-bold">
                    {Math.round(currentPosition * 100)}% Complete
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold">Delhi</span>
                    <div className="w-3 h-3 bg-risk-red rounded-full"></div>
                  </div>
                </div>
                <div className="h-2 bg-white/30 rounded-full overflow-hidden">
                  <motion.div
                    className="h-2 bg-gradient-to-r from-profit-green via-signal-amber to-profit-green rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${currentPosition * 100}%` }}
                    transition={{ duration: 0.5 }}
                  />
                </div>
              </div>
            </div>

            {/* Quick Status Bar */}
            <div className="grid grid-cols-4 gap-1 p-2 bg-gray-100 border-b">
              <div className="bg-white rounded-lg p-2 text-center">
                <Car size={16} className="mx-auto mb-1 text-neuro-blue" />
                <p className="text-xs font-bold">{Math.round(currentPosition * 100)}%</p>
                <p className="text-[10px] text-gray-500">Progress</p>
              </div>
              <div className="bg-white rounded-lg p-2 text-center">
                <Fuel size={16} className="mx-auto mb-1 text-signal-amber" />
                <p className="text-xs font-bold">75%</p>
                <p className="text-[10px] text-gray-500">Fuel</p>
              </div>
              <div className="bg-white rounded-lg p-2 text-center">
                <CloudRain size={16} className="mx-auto mb-1 text-neuro-blue" />
                <p className="text-xs font-bold">Clear</p>
                <p className="text-[10px] text-gray-500">Weather</p>
              </div>
              <div className="bg-white rounded-lg p-2 text-center">
                <Clock size={16} className="mx-auto mb-1 text-profit-green" />
                <p className="text-xs font-bold">18h</p>
                <p className="text-[10px] text-gray-500">ETA</p>
              </div>
            </div>

            {/* Chat Section - Bottom Half */}
            <div className="flex-1 flex flex-col overflow-hidden">
              {/* Chat Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
                {/* Welcome message */}
                <div className="flex gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-neuro-blue to-blue-700 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg">
                    <Brain size={20} className="text-white" />
                  </div>
                  <div className="bg-white rounded-2xl rounded-tl-none p-4 max-w-[85%] shadow-sm border border-gray-100">
                    <p className="text-sm font-medium mb-2">Hi Rajesh! I'm your AI Copilot 🤖</p>
                    <p className="text-sm text-gray-600">I'm actively monitoring your route and will help you with:</p>
                    <div className="grid grid-cols-2 gap-2 mt-3">
                      <div className="flex items-center gap-2 text-xs bg-gray-50 p-2 rounded-lg">
                        <span className="text-lg">🚦</span>
                        <span>Traffic</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs bg-gray-50 p-2 rounded-lg">
                        <span className="text-lg">💰</span>
                        <span>Opportunities</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs bg-gray-50 p-2 rounded-lg">
                        <span className="text-lg">⛽</span>
                        <span>Fuel Stops</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs bg-gray-50 p-2 rounded-lg">
                        <span className="text-lg">😴</span>
                        <span>Rest Breaks</span>
                      </div>
                    </div>
                  </div>
                </div>

                {copilotMessages.map((msg) => (
                  <motion.div
                    key={msg.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex gap-3 ${msg.type === 'user' ? 'flex-row-reverse' : ''}`}
                  >
                    {msg.type === 'agent' && (
                      <div className="w-10 h-10 bg-gradient-to-br from-neuro-blue to-blue-700 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg">
                        <Brain size={20} className="text-white" />
                      </div>
                    )}
                    {msg.type === 'user' && (
                      <div className="w-10 h-10 bg-gradient-to-br from-signal-amber to-orange-500 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg text-white font-bold">
                        R
                      </div>
                    )}
                    <div className={`rounded-2xl p-4 max-w-[85%] shadow-sm ${msg.type === 'agent'
                      ? 'bg-white rounded-tl-none border border-gray-100'
                      : 'bg-gradient-to-r from-neuro-blue to-blue-600 text-white rounded-tr-none'
                      }`}>
                      <p className="text-sm">{msg.message}</p>
                      <p className={`text-xs mt-2 ${msg.type === 'agent' ? 'text-gray-400' : 'text-blue-200'}`}>
                        {msg.time}
                      </p>
                    </div>
                  </motion.div>
                ))}

                {loading && (
                  <div className="flex gap-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-neuro-blue to-blue-700 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg">
                      <Brain size={20} className="text-white animate-pulse" />
                    </div>
                    <div className="bg-white rounded-2xl rounded-tl-none p-4 shadow-sm border border-gray-100">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-neuro-blue rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                        <div className="w-2 h-2 bg-neuro-blue rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                        <div className="w-2 h-2 bg-neuro-blue rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                      </div>
                    </div>
                  </div>
                )}

                <div ref={copilotEndRef} />
              </div>

              {/* Input Area */}
              <div className="bg-white border-t p-4 shadow-lg">
                <div className="flex gap-3">
                  <button className="p-3 bg-gray-100 rounded-full hover:bg-gray-200 transition-colors">
                    <Mic size={22} className="text-gray-600" />
                  </button>
                  <input
                    type="text"
                    placeholder="Ask about traffic, fuel, weather, opportunities..."
                    className="flex-1 px-5 py-3 bg-gray-100 rounded-full focus:outline-none focus:ring-2 focus:ring-neuro-blue text-sm"
                    onKeyPress={async (e) => {
                      if (e.key === 'Enter') {
                        const input = e.target as HTMLInputElement;
                        const userQuery = input.value.trim();
                        if (!userQuery) return;

                        addCopilotMessage('user', userQuery);
                        input.value = '';

                        // Call the real AI copilot API
                        const activeMissionId = currentMissionId || currentMission?.id;

                        if (activeMissionId) {
                          addCopilotMessage('agent', '🔍 Analyzing your request...');

                          try {
                            const result = await copilotChat({
                              mission_id: activeMissionId,
                              query: userQuery,
                            });

                            // Remove the "analyzing" message and add real AI response
                            setCopilotMessages(prev => prev.slice(0, -1));
                            addCopilotMessage('agent', result.response);
                          } catch (error) {
                            setCopilotMessages(prev => prev.slice(0, -1));
                            addCopilotMessage('agent', '❌ Could not connect to AI agent. Please try again.');
                          }
                        } else {
                          addCopilotMessage('agent', '⚠️ No active mission. Start a mission first to get AI assistance.');
                        }
                      }
                    }}
                  />
                  <button
                    onClick={handleAICheck}
                    className="p-3 bg-gradient-to-r from-neuro-blue to-blue-600 text-white rounded-full hover:shadow-lg transition-all"
                    disabled={loading}
                  >
                    <Zap size={22} />
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Settings Page */}
      <AnimatePresence>
        {showSettings && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-white z-50 flex flex-col"
          >
            <div className="bg-gradient-to-r from-neuro-blue to-blue-700 text-white p-4 flex items-center gap-4">
              <button
                onClick={() => setShowSettings(false)}
                className="p-2 hover:bg-white/20 rounded-full transition-colors"
              >
                <X size={24} />
              </button>
              <h2 className="text-xl font-bold">Settings</h2>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              <Card>
                <h3 className="font-bold mb-4 flex items-center gap-2">
                  <Bell size={20} className="text-neuro-blue" />
                  Notifications
                </h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span>Push Notifications</span>
                    <div className="w-12 h-6 bg-profit-green rounded-full relative">
                      <div className="w-5 h-5 bg-white rounded-full absolute right-0.5 top-0.5 shadow" />
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Load Alerts</span>
                    <div className="w-12 h-6 bg-profit-green rounded-full relative">
                      <div className="w-5 h-5 bg-white rounded-full absolute right-0.5 top-0.5 shadow" />
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Traffic Updates</span>
                    <div className="w-12 h-6 bg-profit-green rounded-full relative">
                      <div className="w-5 h-5 bg-white rounded-full absolute right-0.5 top-0.5 shadow" />
                    </div>
                  </div>
                </div>
              </Card>

              <Card>
                <h3 className="font-bold mb-4 flex items-center gap-2">
                  <Brain size={20} className="text-signal-amber" />
                  AI Copilot
                </h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span>Voice Commands</span>
                    <div className="w-12 h-6 bg-gray-300 rounded-full relative">
                      <div className="w-5 h-5 bg-white rounded-full absolute left-0.5 top-0.5 shadow" />
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Auto Suggestions</span>
                    <div className="w-12 h-6 bg-profit-green rounded-full relative">
                      <div className="w-5 h-5 bg-white rounded-full absolute right-0.5 top-0.5 shadow" />
                    </div>
                  </div>
                </div>
              </Card>

              <Card>
                <h3 className="font-bold mb-4 flex items-center gap-2">
                  <MapPin size={20} className="text-neuro-blue" />
                  Navigation
                </h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span>Avoid Toll Roads</span>
                    <div className="w-12 h-6 bg-gray-300 rounded-full relative">
                      <div className="w-5 h-5 bg-white rounded-full absolute left-0.5 top-0.5 shadow" />
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Show Fuel Stations</span>
                    <div className="w-12 h-6 bg-profit-green rounded-full relative">
                      <div className="w-5 h-5 bg-white rounded-full absolute right-0.5 top-0.5 shadow" />
                    </div>
                  </div>
                </div>
              </Card>

              <Card>
                <h3 className="font-bold mb-4">App Version</h3>
                <p className="text-gray-600">Neuro-Logistics v2.0.0</p>
                <p className="text-sm text-gray-400 mt-1">AI-Powered Fleet Management</p>
              </Card>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Help & Support Page */}
      <AnimatePresence>
        {showHelp && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-white z-50 flex flex-col"
          >
            <div className="bg-gradient-to-r from-neuro-blue to-blue-700 text-white p-4 flex items-center gap-4">
              <button
                onClick={() => setShowHelp(false)}
                className="p-2 hover:bg-white/20 rounded-full transition-colors"
              >
                <X size={24} />
              </button>
              <h2 className="text-xl font-bold">Help & Support</h2>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              <Card className="bg-gradient-to-br from-neuro-blue to-blue-700 text-white">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-white/20 rounded-full">
                    <HelpCircle size={32} />
                  </div>
                  <div>
                    <h3 className="font-bold text-lg">24/7 Support</h3>
                    <p className="text-blue-200">We're here to help you</p>
                  </div>
                </div>
              </Card>

              <Card>
                <h3 className="font-bold mb-4">Contact Support</h3>
                <div className="space-y-3">
                  <button className="w-full flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                    <div className="p-2 bg-profit-green/10 rounded-full">
                      <Bell size={20} className="text-profit-green" />
                    </div>
                    <div className="text-left">
                      <p className="font-medium">Call Support</p>
                      <p className="text-sm text-gray-500">1800-XXX-XXXX (Toll Free)</p>
                    </div>
                  </button>
                  <button className="w-full flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                    <div className="p-2 bg-neuro-blue/10 rounded-full">
                      <Brain size={20} className="text-neuro-blue" />
                    </div>
                    <div className="text-left">
                      <p className="font-medium">Ask AI Copilot</p>
                      <p className="text-sm text-gray-500">Get instant answers</p>
                    </div>
                  </button>
                </div>
              </Card>

              <Card>
                <h3 className="font-bold mb-4">FAQs</h3>
                <div className="space-y-2">
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <p className="font-medium">How do I accept a load?</p>
                    <p className="text-sm text-gray-500 mt-1">Tap the notification and press Accept</p>
                  </div>
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <p className="font-medium">How to use AI Copilot?</p>
                    <p className="text-sm text-gray-500 mt-1">Click AI Copilot button or ask any question</p>
                  </div>
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <p className="font-medium">Navigation not working?</p>
                    <p className="text-sm text-gray-500 mt-1">Ensure GPS is enabled in device settings</p>
                  </div>
                </div>
              </Card>

              <Card>
                <h3 className="font-bold mb-4">About</h3>
                <p className="text-gray-600">Neuro-Logistics uses AI to optimize your routes, find loads, and keep you safe on the road.</p>
                <p className="text-sm text-gray-400 mt-2">© 2024 Neuro-Logistics. All rights reserved.</p>
              </Card>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Notifications Page */}
      <AnimatePresence>
        {showNotifications && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-white z-50 flex flex-col"
          >
            <div className="bg-gradient-to-r from-neuro-blue to-blue-700 text-white p-4 flex items-center gap-4">
              <button
                onClick={() => setShowNotifications(false)}
                className="p-2 hover:bg-white/20 rounded-full transition-colors"
              >
                <X size={24} />
              </button>
              <h2 className="text-xl font-bold">Notifications</h2>
              {alerts.length > 0 && (
                <span className="ml-auto bg-signal-amber px-3 py-1 rounded-full text-sm font-medium">
                  {alerts.length} new
                </span>
              )}
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {alerts.length === 0 ? (
                <div className="text-center py-12">
                  <Bell size={48} className="mx-auto text-gray-300 mb-4" />
                  <p className="text-gray-500 font-medium">No notifications</p>
                  <p className="text-gray-400 text-sm mt-1">You're all caught up!</p>
                </div>
              ) : (
                alerts.map((alert) => (
                  <Card key={alert.id} className="border-l-4 border-l-signal-amber">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex items-start gap-3">
                        <div className="p-2 bg-signal-amber/10 rounded-full mt-0.5">
                          {alert.type === 'opportunity' && <DollarSign size={20} className="text-signal-amber" />}
                          {alert.type === 'warning' && <AlertTriangle size={20} className="text-risk-red" />}
                          {alert.type === 'reroute' && <Navigation size={20} className="text-neuro-blue" />}
                          {!['opportunity', 'warning', 'reroute'].includes(alert.type) && <Bell size={20} className="text-signal-amber" />}
                        </div>
                        <div>
                          <h4 className="font-bold text-gray-900">{alert.title}</h4>
                          <p className="text-sm text-gray-600 mt-1">{alert.message}</p>
                          {alert.extraPay && (
                            <p className="text-sm text-profit-green font-medium mt-2">+₹{alert.extraPay.toLocaleString()} extra</p>
                          )}
                          <p className="text-xs text-gray-400 mt-2">
                            {new Date(alert.timestamp).toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => removeAlert(alert.id)}
                        className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                      >
                        <X size={18} />
                      </button>
                    </div>
                    {alert.type === 'opportunity' && (
                      <div className="mt-3 flex gap-2">
                        <Button
                          variant="success"
                          size="sm"
                          className="flex-1"
                          onClick={() => {
                            setEarnings(prev => prev + (alert.extraPay || 2500));
                            removeAlert(alert.id);
                            setShowNotifications(false);
                          }}
                        >
                          Accept
                        </Button>
                        <Button
                          variant="secondary"
                          size="sm"
                          className="flex-1"
                          onClick={() => removeAlert(alert.id)}
                        >
                          Decline
                        </Button>
                      </div>
                    )}
                  </Card>
                ))
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Opportunity Alert Modal */}
      <AnimatePresence>
        {showAlert && alerts.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-end md:items-center justify-center p-4 z-50"
          >
            <motion.div
              initial={{ y: 100, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: 100, opacity: 0 }}
              className="bg-white rounded-2xl p-6 w-full max-w-md border-4 border-signal-amber shadow-2xl"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 bg-signal-amber rounded-full animate-pulse" />
                  <h3 className="text-xl font-bold">{alerts[0].title}</h3>
                </div>
                <button onClick={handleRejectOpportunity}>
                  <X size={24} />
                </button>
              </div>

              <p className="text-gray-700 mb-4">{alerts[0].message}</p>

              <div className="bg-gray-50 rounded-lg p-4 space-y-2 mb-6">
                <div className="flex justify-between">
                  <span className="text-gray-600">Pickup Location:</span>
                  <span className="font-semibold">{alerts[0].pickup}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Extra Pay:</span>
                  <span className="font-bold text-profit-green text-lg">₹{alerts[0].extraPay?.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Detour Time:</span>
                  <span className="font-semibold text-signal-amber">{alerts[0].detour}</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <Button variant="danger" className="w-full" onClick={handleRejectOpportunity}>
                  Reject
                </Button>
                <Button variant="success" className="w-full" onClick={handleAcceptOpportunity}>
                  Accept
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Bottom Navigation (when not in navigation view) */}
      {!showNavigation && !showCopilot && (
        <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4 grid grid-cols-2 gap-4">
          <button
            onClick={handleNavigate}
            className="flex flex-col items-center gap-1 text-neuro-blue p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Navigation size={24} />
            <span className="text-xs font-medium">Navigate</span>
          </button>
          <button
            onClick={() => setShowCopilot(true)}
            className="flex flex-col items-center gap-1 text-signal-amber p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Brain size={24} />
            <span className="text-xs font-medium">AI Copilot</span>
          </button>
        </div>
      )}
    </div>
  );
}
