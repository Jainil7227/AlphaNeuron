import { useState } from 'react';
import {
    CalculatorIcon,
    TruckIcon,
    MapPinIcon,
    CurrencyRupeeIcon,
    ClockIcon,
    ChartBarIcon,
    ArrowPathIcon,
    SparklesIcon,
} from '@heroicons/react/24/outline';
import api from '../api';

interface CostResult {
    success: boolean;
    agent_used: boolean;
    calculation: {
        origin: string;
        destination: string;
        cargo: { type: string; weight_tons: number };
        vehicle_type: string;
        route: {
            distance_km: number;
            duration_hours: number;
            highways: string[];
            toll_plazas: number;
            border_crossings: number;
        };
        cost_breakdown: {
            fuel: { liters_needed: number; price_per_liter: number; total: number };
            tolls: number;
            driver: number;
            misc: number;
            total_operating_cost: number;
        };
        fare_calculation: {
            base_fare: number;
            effort_multiplier: number;
            adjusted_fare: number;
            fuel_surcharge: number;
            toll_pass_through: number;
            total_fare: number;
            rate_per_km: number;
        };
        profit_analysis: {
            gross_profit: number;
            profit_margin_percent: number;
        };
        eta_range: {
            optimistic: { hours: number; arrival: string };
            expected: { hours: number; arrival: string };
            pessimistic: { hours: number; arrival: string };
        };
        return_journey: {
            distance_km: number;
            empty_return_cost: { total: number };
            potential_backhaul_earnings: number;
        } | null;
    };
    ai_insights: string[];
    ai_raw_analysis: any | null;
}

const INDIAN_CITIES = [
    'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata',
    'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow', 'Surat', 'Kanpur',
    'Nagpur', 'Indore', 'Bhopal', 'Vadodara', 'Coimbatore', 'Kochi'
];

const CARGO_TYPES = [
    'General', 'Electronics', 'Textiles', 'Perishable', 'Fragile',
    'Chemicals', 'Hazmat', 'Machinery', 'Automobiles', 'FMCG'
];

const VEHICLE_TYPES = [
    { value: 'LCV', label: 'LCV (Light Commercial Vehicle)', capacity: '1-7 tons' },
    { value: 'MAV', label: 'MAV (Medium Articulated Vehicle)', capacity: '7-15 tons' },
    { value: 'HCV', label: 'HCV (Heavy Commercial Vehicle)', capacity: '15-40 tons' },
];

const CostCalculatorPage: React.FC = () => {
    const [origin, setOrigin] = useState('');
    const [destination, setDestination] = useState('');
    const [weightTons, setWeightTons] = useState(10);
    const [cargoType, setCargoType] = useState('General');
    const [vehicleType, setVehicleType] = useState('HCV');
    const [includeReturn, setIncludeReturn] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [result, setResult] = useState<CostResult | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleCalculate = async () => {
        if (!origin || !destination) {
            setError('Please select both origin and destination cities');
            return;
        }

        if (origin === destination) {
            setError('Origin and destination cannot be the same');
            return;
        }

        setIsLoading(true);
        setError(null);

        try {
            const response = await api.post('/api/v1/agent/calculate-cost', {
                origin,
                destination,
                weight_tons: weightTons,
                cargo_type: cargoType,
                vehicle_type: vehicleType,
                include_return: includeReturn,
            });
            setResult(response.data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to calculate cost');
        } finally {
            setIsLoading(false);
        }
    };

    const handleReset = () => {
        setOrigin('');
        setDestination('');
        setWeightTons(10);
        setCargoType('General');
        setVehicleType('HCV');
        setIncludeReturn(false);
        setResult(null);
        setError(null);
    };

    return (
        <div className="space-y-6">
            {/* Page Header */}
            <div className="flex items-center gap-3">
                <div className="h-12 w-12 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
                    <CalculatorIcon className="h-6 w-6 text-white" />
                </div>
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Cost Calculator</h1>
                    <p className="text-gray-600">AI-powered trip cost estimation using Neuro-Logistics Agent</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Input Form */}
                <div className="lg:col-span-1 space-y-4">
                    <div className="card">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                            <MapPinIcon className="h-5 w-5 text-purple-600" />
                            Route Details
                        </h3>

                        {/* Origin */}
                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Origin City
                            </label>
                            <select
                                value={origin}
                                onChange={(e) => setOrigin(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                            >
                                <option value="">Select origin city</option>
                                {INDIAN_CITIES.map((city) => (
                                    <option key={city} value={city}>{city}</option>
                                ))}
                            </select>
                        </div>

                        {/* Destination */}
                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Destination City
                            </label>
                            <select
                                value={destination}
                                onChange={(e) => setDestination(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                            >
                                <option value="">Select destination city</option>
                                {INDIAN_CITIES.map((city) => (
                                    <option key={city} value={city}>{city}</option>
                                ))}
                            </select>
                        </div>

                        {/* Weight */}
                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Cargo Weight: {weightTons} tons
                            </label>
                            <input
                                type="range"
                                min="1"
                                max="40"
                                value={weightTons}
                                onChange={(e) => setWeightTons(Number(e.target.value))}
                                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
                            />
                            <div className="flex justify-between text-xs text-gray-500 mt-1">
                                <span>1 ton</span>
                                <span>40 tons</span>
                            </div>
                        </div>

                        {/* Cargo Type */}
                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Cargo Type
                            </label>
                            <select
                                value={cargoType}
                                onChange={(e) => setCargoType(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                            >
                                {CARGO_TYPES.map((type) => (
                                    <option key={type} value={type}>{type}</option>
                                ))}
                            </select>
                        </div>

                        {/* Vehicle Type */}
                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Vehicle Type
                            </label>
                            <select
                                value={vehicleType}
                                onChange={(e) => setVehicleType(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                            >
                                {VEHICLE_TYPES.map((type) => (
                                    <option key={type.value} value={type.value}>
                                        {type.label} ({type.capacity})
                                    </option>
                                ))}
                            </select>
                        </div>

                        {/* Include Return */}
                        <div className="mb-6">
                            <label className="flex items-center gap-2 cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={includeReturn}
                                    onChange={(e) => setIncludeReturn(e.target.checked)}
                                    className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                                />
                                <span className="text-sm text-gray-700">Include return journey analysis</span>
                            </label>
                        </div>

                        {/* Error Message */}
                        {error && (
                            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                                {error}
                            </div>
                        )}

                        {/* Buttons */}
                        <div className="flex gap-2">
                            <button
                                onClick={handleCalculate}
                                disabled={isLoading}
                                className="flex-1 flex items-center justify-center gap-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-3 px-4 rounded-lg font-semibold hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50 transition-all"
                            >
                                {isLoading ? (
                                    <>
                                        <ArrowPathIcon className="h-5 w-5 animate-spin" />
                                        Calculating...
                                    </>
                                ) : (
                                    <>
                                        <CalculatorIcon className="h-5 w-5" />
                                        Calculate Cost
                                    </>
                                )}
                            </button>
                            <button
                                onClick={handleReset}
                                className="px-4 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-all"
                            >
                                Reset
                            </button>
                        </div>
                    </div>
                </div>

                {/* Results */}
                <div className="lg:col-span-2 space-y-4">
                    {result ? (
                        <>
                            {/* Route Summary */}
                            <div className="card bg-gradient-to-br from-purple-50 to-indigo-50 border-purple-200">
                                <div className="flex items-center justify-between mb-4">
                                    <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                                        <TruckIcon className="h-5 w-5 text-purple-600" />
                                        Route: {result.calculation.origin} → {result.calculation.destination}
                                    </h3>
                                    <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium">
                                        {result.calculation.vehicle_type}
                                    </span>
                                </div>
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                    <div className="bg-white p-3 rounded-lg">
                                        <p className="text-xs text-gray-500">Distance</p>
                                        <p className="text-xl font-bold text-gray-900">{result.calculation.route.distance_km} km</p>
                                    </div>
                                    <div className="bg-white p-3 rounded-lg">
                                        <p className="text-xs text-gray-500">Duration</p>
                                        <p className="text-xl font-bold text-gray-900">{result.calculation.route.duration_hours} hrs</p>
                                    </div>
                                    <div className="bg-white p-3 rounded-lg">
                                        <p className="text-xs text-gray-500">Toll Plazas</p>
                                        <p className="text-xl font-bold text-gray-900">{result.calculation.route.toll_plazas}</p>
                                    </div>
                                    <div className="bg-white p-3 rounded-lg">
                                        <p className="text-xs text-gray-500">Highways</p>
                                        <p className="text-sm font-medium text-gray-900">{result.calculation.route.highways.slice(0, 2).join(', ')}</p>
                                    </div>
                                </div>
                            </div>

                            {/* Cost Breakdown & Fare */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {/* Cost Breakdown */}
                                <div className="card">
                                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                                        <CurrencyRupeeIcon className="h-5 w-5 text-orange-600" />
                                        Operating Cost
                                    </h3>
                                    <div className="space-y-3">
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Fuel ({result.calculation.cost_breakdown.fuel.liters_needed}L)</span>
                                            <span className="font-semibold">₹{result.calculation.cost_breakdown.fuel.total.toLocaleString()}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Toll Charges</span>
                                            <span className="font-semibold">₹{result.calculation.cost_breakdown.tolls.toLocaleString()}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Driver Cost</span>
                                            <span className="font-semibold">₹{result.calculation.cost_breakdown.driver.toLocaleString()}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Misc (Maintenance)</span>
                                            <span className="font-semibold">₹{result.calculation.cost_breakdown.misc.toLocaleString()}</span>
                                        </div>
                                        <div className="border-t pt-3 flex justify-between">
                                            <span className="font-semibold text-gray-900">Total Operating Cost</span>
                                            <span className="font-bold text-orange-600">₹{result.calculation.cost_breakdown.total_operating_cost.toLocaleString()}</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Fare Calculation */}
                                <div className="card">
                                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                                        <ChartBarIcon className="h-5 w-5 text-green-600" />
                                        Recommended Fare
                                    </h3>
                                    <div className="space-y-3">
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Base Fare</span>
                                            <span className="font-semibold">₹{result.calculation.fare_calculation.base_fare.toLocaleString()}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Effort Multiplier</span>
                                            <span className="font-semibold">{result.calculation.fare_calculation.effort_multiplier}x</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Fuel Surcharge</span>
                                            <span className="font-semibold">₹{result.calculation.fare_calculation.fuel_surcharge.toLocaleString()}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Rate per km</span>
                                            <span className="font-semibold">₹{result.calculation.fare_calculation.rate_per_km}/km</span>
                                        </div>
                                        <div className="border-t pt-3 flex justify-between">
                                            <span className="font-semibold text-gray-900">Total Fare</span>
                                            <span className="font-bold text-2xl text-green-600">₹{result.calculation.fare_calculation.total_fare.toLocaleString()}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Profit & ETA */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {/* Profit Analysis */}
                                <div className="card bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
                                    <h3 className="text-lg font-semibold text-gray-900 mb-4">💰 Profit Analysis</h3>
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <p className="text-sm text-gray-600">Gross Profit</p>
                                            <p className="text-3xl font-bold text-green-600">₹{result.calculation.profit_analysis.gross_profit.toLocaleString()}</p>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-sm text-gray-600">Profit Margin</p>
                                            <p className="text-3xl font-bold text-emerald-600">{result.calculation.profit_analysis.profit_margin_percent}%</p>
                                        </div>
                                    </div>
                                </div>

                                {/* ETA Range */}
                                <div className="card">
                                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                                        <ClockIcon className="h-5 w-5 text-blue-600" />
                                        ETA Range
                                    </h3>
                                    <div className="space-y-2">
                                        <div className="flex justify-between items-center p-2 bg-green-50 rounded">
                                            <span className="text-green-700">Optimistic</span>
                                            <span className="font-semibold">{result.calculation.eta_range.optimistic.hours} hrs</span>
                                        </div>
                                        <div className="flex justify-between items-center p-2 bg-blue-50 rounded">
                                            <span className="text-blue-700">Expected</span>
                                            <span className="font-semibold">{result.calculation.eta_range.expected.hours} hrs</span>
                                        </div>
                                        <div className="flex justify-between items-center p-2 bg-orange-50 rounded">
                                            <span className="text-orange-700">Pessimistic</span>
                                            <span className="font-semibold">{result.calculation.eta_range.pessimistic.hours} hrs</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Return Journey */}
                            {result.calculation.return_journey && (
                                <div className="card bg-gradient-to-br from-amber-50 to-orange-50 border-amber-200">
                                    <h3 className="text-lg font-semibold text-gray-900 mb-4">🔄 Return Journey Analysis</h3>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <p className="text-sm text-gray-600">Empty Return Cost</p>
                                            <p className="text-2xl font-bold text-red-600">-₹{result.calculation.return_journey.empty_return_cost.total.toLocaleString()}</p>
                                        </div>
                                        <div>
                                            <p className="text-sm text-gray-600">Potential Backhaul Earnings</p>
                                            <p className="text-2xl font-bold text-green-600">+₹{result.calculation.return_journey.potential_backhaul_earnings.toLocaleString()}</p>
                                        </div>
                                    </div>
                                    <p className="mt-3 text-sm text-amber-700 bg-amber-100 p-2 rounded">
                                        💡 Book a backhaul load to avoid ₹{result.calculation.return_journey.empty_return_cost.total.toLocaleString()} in dead miles!
                                    </p>
                                </div>
                            )}

                            {/* AI Insights */}
                            <div className="card">
                                <div className="flex items-center justify-between mb-4">
                                    <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                                        <SparklesIcon className="h-5 w-5 text-purple-600" />
                                        AI Agent Insights
                                    </h3>
                                    {result.agent_used ? (
                                        <span className="flex items-center gap-1 px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                                            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                                            Grok AI Active
                                        </span>
                                    ) : (
                                        <span className="flex items-center gap-1 px-3 py-1 bg-yellow-100 text-yellow-700 rounded-full text-sm font-medium">
                                            <span className="w-2 h-2 bg-yellow-500 rounded-full"></span>
                                            Calculated Mode
                                        </span>
                                    )}
                                </div>
                                <div className="space-y-2">
                                    {result.ai_insights.map((insight, index) => (
                                        <div key={index} className={`flex items-start gap-2 p-2 rounded-lg ${result.agent_used ? 'bg-gradient-to-r from-purple-50 to-indigo-50' : 'bg-gray-50'}`}>
                                            <span className="text-purple-600">•</span>
                                            <span className="text-sm text-gray-700">{insight}</span>
                                        </div>
                                    ))}
                                </div>
                                {result.agent_used && (
                                    <p className="mt-4 text-xs text-gray-500 text-center">
                                        ✨ Powered by Grok AI - Neuro-Logistics Supervisor Agent
                                    </p>
                                )}
                            </div>
                        </>
                    ) : (
                        <div className="card h-full flex flex-col items-center justify-center text-center py-16">
                            <div className="h-20 w-20 bg-purple-100 rounded-full flex items-center justify-center mb-4">
                                <CalculatorIcon className="h-10 w-10 text-purple-600" />
                            </div>
                            <h3 className="text-xl font-semibold text-gray-900 mb-2">Calculate Trip Cost</h3>
                            <p className="text-gray-600 max-w-md">
                                Select origin, destination, and cargo details to get AI-powered cost estimation
                                with route analysis, fare recommendations, and profit insights.
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default CostCalculatorPage;
