import { useState, useEffect } from 'react';
import { MapPin, Package, DollarSign, Clock, Shield, Zap, TrendingDown, AlertTriangle, Loader2, Weight } from 'lucide-react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { useStore } from '../../store/useStore';

export function MissionPlanner() {
  const {
    cities,
    fetchRoutes,
    planNewMission,
    currentMissionPlan,
    loading,
    error
  } = useStore();

  const [origin, setOrigin] = useState('Mumbai');
  const [destination, setDestination] = useState('Delhi');
  const [cargoType, setCargoType] = useState('Electronics');
  const [weightTons, setWeightTons] = useState(15);
  const [showResults, setShowResults] = useState(false);

  useEffect(() => {
    fetchRoutes();
  }, [fetchRoutes]);

  const handlePlanMission = async () => {
    const plan = await planNewMission(origin, destination, cargoType, weightTons);
    if (plan) {
      setShowResults(true);
    }
  };

  const cargoTypes = [
    'Electronics', 'Pharmaceuticals', 'FMCG', 'Textiles',
    'Auto Parts', 'Machinery', 'Chemicals', 'Perishables'
  ];

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Mission Planner</h1>
        <p className="text-gray-600">AI-powered route optimization with context-aware dynamic pricing</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3">
          <AlertTriangle className="text-red-500" size={20} />
          <span className="text-red-700">{error}</span>
        </div>
      )}

      <Card>
        <h3 className="font-bold text-lg mb-4">Plan New Mission</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Origin</label>
            <div className="relative">
              <MapPin className="absolute left-3 top-3 text-gray-400" size={18} />
              <select
                value={origin}
                onChange={(e) => setOrigin(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-neuro-blue focus:border-transparent appearance-none bg-white"
              >
                {cities.map((city) => (
                  <option key={city} value={city}>{city}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Destination</label>
            <div className="relative">
              <MapPin className="absolute left-3 top-3 text-gray-400" size={18} />
              <select
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-neuro-blue focus:border-transparent appearance-none bg-white"
              >
                {cities.filter(c => c !== origin).map((city) => (
                  <option key={city} value={city}>{city}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Cargo Type</label>
            <div className="relative">
              <Package className="absolute left-3 top-3 text-gray-400" size={18} />
              <select
                value={cargoType}
                onChange={(e) => setCargoType(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-neuro-blue focus:border-transparent appearance-none bg-white"
              >
                {cargoTypes.map((type) => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Weight (tons)</label>
            <div className="relative">
              <Weight className="absolute left-3 top-3 text-gray-400" size={18} />
              <input
                type="number"
                min="0.5"
                max="25"
                step="0.5"
                value={weightTons}
                onChange={(e) => setWeightTons(parseFloat(e.target.value))}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-neuro-blue focus:border-transparent"
              />
            </div>
          </div>
        </div>

        <Button
          onClick={handlePlanMission}
          variant="primary"
          className="w-full md:w-auto flex items-center justify-center gap-2"
          disabled={loading}
        >
          {loading ? (
            <>
              <Loader2 className="animate-spin" size={18} />
              Analyzing with AI...
            </>
          ) : (
            'Generate Smart Plan'
          )}
        </Button>
      </Card>

      {showResults && currentMissionPlan && (
        <>
          {/* Route Info */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="lg:col-span-2">
              <h3 className="font-bold text-lg mb-4">Route Details</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-500">Distance</p>
                  <p className="text-2xl font-bold font-mono">{currentMissionPlan.route.distance_km} km</p>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-500">Toll Plazas</p>
                  <p className="text-2xl font-bold font-mono">{currentMissionPlan.route.toll_plazas}</p>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-500">Toll Cost</p>
                  <p className="text-2xl font-bold font-mono text-signal-amber">₹{currentMissionPlan.route.toll_cost}</p>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-500">Fuel Stops</p>
                  <p className="text-2xl font-bold font-mono">{currentMissionPlan.route.fuel_stops}</p>
                </div>
              </div>

              <div className="mb-4">
                <p className="text-sm text-gray-500 mb-2">Highways</p>
                <div className="flex flex-wrap gap-2">
                  {currentMissionPlan.route.highways?.map((hw: string, i: number) => (
                    <span key={i} className="px-3 py-1 bg-neuro-blue/10 text-neuro-blue rounded-full text-sm">
                      {hw}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <p className="text-sm text-gray-500 mb-2">Checkpoints / Border Crossings</p>
                <div className="flex flex-wrap gap-2">
                  {currentMissionPlan.route.checkpoints?.map((cp: string, i: number) => (
                    <span key={i} className="px-3 py-1 bg-signal-amber/10 text-signal-amber rounded-full text-sm">
                      {cp}
                    </span>
                  ))}
                </div>
              </div>
            </Card>

            {/* Risk Assessment */}
            <Card className={`border-2 ${currentMissionPlan.risk_assessment.level === 'low' ? 'border-profit-green' :
                currentMissionPlan.risk_assessment.level === 'medium' ? 'border-signal-amber' :
                  'border-risk-red'
              }`}>
              <div className="flex items-center gap-3 mb-4">
                <Shield size={24} className={
                  currentMissionPlan.risk_assessment.level === 'low' ? 'text-profit-green' :
                    currentMissionPlan.risk_assessment.level === 'medium' ? 'text-signal-amber' :
                      'text-risk-red'
                } />
                <div>
                  <h3 className="font-bold text-lg">Risk Assessment</h3>
                  <p className={`text-sm font-semibold ${currentMissionPlan.risk_assessment.level === 'low' ? 'text-profit-green' :
                      currentMissionPlan.risk_assessment.level === 'medium' ? 'text-signal-amber' :
                        'text-risk-red'
                    }`}>
                    {currentMissionPlan.risk_assessment.level.toUpperCase()} (Score: {currentMissionPlan.risk_assessment.score}/100)
                  </p>
                </div>
              </div>

              <div className="mb-4">
                <p className="text-sm text-gray-500 mb-2">Risk Factors</p>
                <ul className="space-y-1">
                  {currentMissionPlan.risk_assessment.factors?.map((factor: string, i: number) => (
                    <li key={i} className="text-sm flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-signal-amber rounded-full" />
                      {factor}
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <p className="text-sm text-gray-500 mb-2">Recommendations</p>
                <ul className="space-y-1">
                  {currentMissionPlan.risk_assessment.recommendations?.map((rec: string, i: number) => (
                    <li key={i} className="text-sm flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-profit-green rounded-full" />
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            </Card>
          </div>

          {/* ETA Range */}
          <Card>
            <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
              <Clock size={20} />
              ETA Range (Context-Aware)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-profit-green/10 rounded-lg border-2 border-profit-green">
                <Zap className="mx-auto text-profit-green mb-2" size={24} />
                <p className="text-sm text-gray-600">Optimistic</p>
                <p className="text-2xl font-bold font-mono">{currentMissionPlan.eta_range.optimistic?.hours?.toFixed(1)}h</p>
                <p className="text-xs text-gray-500 mt-1">Best case scenario</p>
              </div>
              <div className="text-center p-4 bg-neuro-blue/10 rounded-lg border-2 border-neuro-blue">
                <Clock className="mx-auto text-neuro-blue mb-2" size={24} />
                <p className="text-sm text-gray-600">Expected</p>
                <p className="text-2xl font-bold font-mono">{currentMissionPlan.eta_range.expected?.hours?.toFixed(1)}h</p>
                <p className="text-xs text-gray-500 mt-1">Most likely</p>
              </div>
              <div className="text-center p-4 bg-signal-amber/10 rounded-lg border-2 border-signal-amber">
                <TrendingDown className="mx-auto text-signal-amber mb-2" size={24} />
                <p className="text-sm text-gray-600">Pessimistic</p>
                <p className="text-2xl font-bold font-mono">{currentMissionPlan.eta_range.pessimistic?.hours?.toFixed(1)}h</p>
                <p className="text-xs text-gray-500 mt-1">Worst case</p>
              </div>
            </div>
          </Card>

          {/* Dynamic Fare */}
          <Card className="border-2 border-profit-green">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <DollarSign size={24} className="text-profit-green" />
                <div>
                  <h3 className="font-bold text-lg">Dynamic Fare (Effort-Based)</h3>
                  <p className="text-sm text-gray-600">Priced on effort, not just distance</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-3xl font-bold font-mono text-profit-green">
                  ₹{currentMissionPlan.fare.calculated?.total_fare?.toLocaleString()}
                </p>
                <p className="text-sm text-gray-500">
                  ₹{currentMissionPlan.fare.calculated?.per_km_rate?.toFixed(2)}/km
                </p>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4 space-y-2">
              <h4 className="font-semibold text-sm mb-3">Price Breakdown</h4>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Base Fare</span>
                  <span className="font-mono">₹{currentMissionPlan.fare.calculated?.base_fare?.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Effort Multiplier</span>
                  <span className="font-mono text-signal-amber">{currentMissionPlan.fare.calculated?.effort_multiplier?.toFixed(2)}x</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Adjusted Base</span>
                  <span className="font-mono">₹{currentMissionPlan.fare.calculated?.adjusted_base?.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Toll Cost</span>
                  <span className="font-mono">₹{currentMissionPlan.fare.calculated?.toll_cost?.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Fuel Estimate</span>
                  <span className="font-mono">₹{currentMissionPlan.fare.calculated?.fuel_estimate?.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Driver Allowance</span>
                  <span className="font-mono">₹{currentMissionPlan.fare.calculated?.driver_allowance?.toLocaleString()}</span>
                </div>
              </div>
            </div>
          </Card>

          {/* AI Insights */}
          {currentMissionPlan.ai_insights && (
            <Card className="bg-gradient-to-r from-neuro-blue to-blue-700 text-white">
              <div className="flex items-start gap-4">
                <div className="p-2 bg-white/20 rounded-lg">
                  <Zap size={24} className="text-signal-amber" />
                </div>
                <div>
                  <h3 className="font-bold text-lg mb-2">AI Insights</h3>
                  {currentMissionPlan.ai_insights.summary && (
                    <p className="text-blue-100 mb-4">{currentMissionPlan.ai_insights.summary}</p>
                  )}
                  {currentMissionPlan.ai_insights.tips && (
                    <div className="flex flex-wrap gap-2">
                      {currentMissionPlan.ai_insights.tips.map((tip: string, i: number) => (
                        <span key={i} className="px-3 py-1 bg-white/20 rounded-full text-sm">
                          {tip}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </Card>
          )}

          {/* Return Load Options */}
          {currentMissionPlan.return_load_options && currentMissionPlan.return_load_options.length > 0 && (
            <Card>
              <h3 className="font-bold text-lg mb-4">Pre-Identified Return Loads</h3>
              <p className="text-sm text-gray-600 mb-4">
                Avoid empty miles! These loads are available for your return journey.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {currentMissionPlan.return_load_options.slice(0, 3).map((load: any, i: number) => (
                  <div key={i} className="p-4 bg-gray-50 rounded-lg border border-gray-200 hover:border-neuro-blue transition-colors">
                    <p className="font-semibold">{load.cargo_type}</p>
                    <p className="text-sm text-gray-600">{load.pickup_city} → {load.delivery_city}</p>
                    <div className="flex justify-between mt-2">
                      <span className="text-sm text-gray-500">{load.weight_tons} tons</span>
                      <span className="font-bold text-profit-green">₹{load.offered_rate?.toLocaleString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Action Buttons */}
          <div className="flex gap-4">
            <Button variant="success" className="flex-1">
              Accept & Start Mission
            </Button>
            <Button variant="danger" className="flex-1" onClick={() => setShowResults(false)}>
              Cancel
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
