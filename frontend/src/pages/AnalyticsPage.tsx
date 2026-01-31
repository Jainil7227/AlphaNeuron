import { useEffect, useState } from 'react';
import { analyticsApi } from '../api';
import { FleetMetrics, RevenueMetrics } from '../types';
import {
    ChartBarIcon,
    TruckIcon,
    CurrencyDollarIcon,
    ClockIcon,
} from '@heroicons/react/24/outline';
import { formatCurrency, formatDistance } from '../utils/formatters';

const AnalyticsPage: React.FC = () => {
    const [fleetMetrics, setFleetMetrics] = useState<FleetMetrics | null>(null);
    const [revenueMetrics, setRevenueMetrics] = useState<RevenueMetrics | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchAnalytics = async () => {
            try {
                const [fleet, revenue] = await Promise.all([
                    analyticsApi.getFleetMetrics(),
                    analyticsApi.getRevenue(),
                ]);
                setFleetMetrics(fleet);
                setRevenueMetrics(revenue);
            } catch (error) {
                console.error('Failed to fetch analytics:', error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchAnalytics();
    }, []);

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Page Header */}
            <div>
                <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
                <p className="text-gray-600 mt-1">Performance metrics and insights</p>
            </div>

            {/* Fleet Analytics */}
            <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Fleet Performance</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <div className="card">
                        <div className="flex items-center justify-between mb-2">
                            <TruckIcon className="h-8 w-8 text-blue-600" />
                            <span className="text-2xl font-bold text-blue-600">
                                {fleetMetrics?.totalVehicles || 0}
                            </span>
                        </div>
                        <p className="text-sm font-medium text-gray-600">Total Vehicles</p>
                    </div>

                    <div className="card">
                        <div className="flex items-center justify-between mb-2">
                            <ChartBarIcon className="h-8 w-8 text-green-600" />
                            <span className="text-2xl font-bold text-green-600">
                                {fleetMetrics?.averageUtilization.toFixed(1) || 0}%
                            </span>
                        </div>
                        <p className="text-sm font-medium text-gray-600">Avg Utilization</p>
                    </div>

                    <div className="card">
                        <div className="flex items-center justify-between mb-2">
                            <ClockIcon className="h-8 w-8 text-purple-600" />
                            <span className="text-2xl font-bold text-purple-600">
                                {fleetMetrics?.activeVehicles || 0}
                            </span>
                        </div>
                        <p className="text-sm font-medium text-gray-600">Active Now</p>
                    </div>

                    <div className="card">
                        <div className="flex items-center justify-between mb-2">
                            <TruckIcon className="h-8 w-8 text-gray-600" />
                            <span className="text-2xl font-bold text-gray-600">
                                {fleetMetrics?.idleVehicles || 0}
                            </span>
                        </div>
                        <p className="text-sm font-medium text-gray-600">Idle Vehicles</p>
                    </div>
                </div>
            </div>

            {/* Distance & Efficiency */}
            <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Distance & Efficiency</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="card">
                        <p className="text-sm font-medium text-gray-600 mb-2">Total Distance Covered</p>
                        <p className="text-3xl font-bold text-gray-900">
                            {formatDistance(fleetMetrics?.totalDistanceCovered || 0)}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">All time</p>
                    </div>

                    <div className="card">
                        <p className="text-sm font-medium text-gray-600 mb-2">Avg Distance/Vehicle</p>
                        <p className="text-3xl font-bold text-gray-900">
                            {formatDistance(
                                fleetMetrics?.totalVehicles
                                    ? (fleetMetrics.totalDistanceCovered / fleetMetrics.totalVehicles)
                                    : 0
                            )}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">Per vehicle</p>
                    </div>

                    <div className="card">
                        <p className="text-sm font-medium text-gray-600 mb-2">Vehicles in Maintenance</p>
                        <p className="text-3xl font-bold text-orange-600">
                            {fleetMetrics?.maintenanceVehicles || 0}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">Undergoing service</p>
                    </div>
                </div>
            </div>

            {/* Revenue Analytics */}
            <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Revenue Analytics</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="card">
                        <div className="flex items-center space-x-2 mb-2">
                            <CurrencyDollarIcon className="h-6 w-6 text-amber-600" />
                            <p className="text-sm font-medium text-gray-600">Today's Revenue</p>
                        </div>
                        <p className="text-3xl font-bold text-amber-600">
                            {formatCurrency(revenueMetrics?.todayRevenue || 0)}
                        </p>
                    </div>

                    <div className="card">
                        <div className="flex items-center space-x-2 mb-2">
                            <CurrencyDollarIcon className="h-6 w-6 text-green-600" />
                            <p className="text-sm font-medium text-gray-600">This Week</p>
                        </div>
                        <p className="text-3xl font-bold text-green-600">
                            {formatCurrency(revenueMetrics?.weekRevenue || 0)}
                        </p>
                    </div>

                    <div className="card">
                        <div className="flex items-center space-x-2 mb-2">
                            <CurrencyDollarIcon className="h-6 w-6 text-blue-600" />
                            <p className="text-sm font-medium text-gray-600">This Month</p>
                        </div>
                        <p className="text-3xl font-bold text-blue-600">
                            {formatCurrency(revenueMetrics?.monthRevenue || 0)}
                        </p>
                    </div>
                </div>
            </div>

            {/* Status Summary */}
            <div className="card">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Fleet Status Summary</h2>
                <div className="space-y-4">
                    <div>
                        <div className="flex justify-between text-sm mb-2">
                            <span className="text-gray-600">Active Vehicles</span>
                            <span className="font-semibold text-gray-900">
                                {fleetMetrics?.activeVehicles || 0} / {fleetMetrics?.totalVehicles || 0}
                            </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3">
                            <div
                                className="bg-green-500 h-3 rounded-full"
                                style={{
                                    width: `${fleetMetrics?.totalVehicles
                                            ? (fleetMetrics.activeVehicles / fleetMetrics.totalVehicles) * 100
                                            : 0
                                        }%`,
                                }}
                            ></div>
                        </div>
                    </div>

                    <div>
                        <div className="flex justify-between text-sm mb-2">
                            <span className="text-gray-600">Average Utilization</span>
                            <span className="font-semibold text-gray-900">
                                {fleetMetrics?.averageUtilization.toFixed(1) || 0}%
                            </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3">
                            <div
                                className="bg-purple-500 h-3 rounded-full"
                                style={{ width: `${fleetMetrics?.averageUtilization || 0}%` }}
                            ></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AnalyticsPage;
