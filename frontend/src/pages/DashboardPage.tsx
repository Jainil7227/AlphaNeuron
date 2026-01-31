import { useEffect, useState } from 'react';
import { analyticsApi } from '../api';
import { FleetMetrics, RevenueMetrics } from '../types';
import {
    TruckIcon,
    CubeIcon,
    CurrencyDollarIcon,
    ChartBarIcon,
} from '@heroicons/react/24/outline';

const DashboardPage: React.FC = () => {
    const [fleetMetrics, setFleetMetrics] = useState<FleetMetrics | null>(null);
    const [revenueMetrics, setRevenueMetrics] = useState<RevenueMetrics | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchMetrics = async () => {
            try {
                const [fleet, revenue] = await Promise.all([
                    analyticsApi.getFleetMetrics(),
                    analyticsApi.getRevenue(),
                ]);
                setFleetMetrics(fleet);
                setRevenueMetrics(revenue);
            } catch (error) {
                console.error('Failed to fetch metrics:', error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchMetrics();
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
                <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
                <p className="text-gray-600 mt-1">Overview of your logistics operations</p>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {/* Total Vehicles */}
                <div className="card">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-600">Total Vehicles</p>
                            <p className="text-3xl font-bold text-gray-900 mt-2">
                                {fleetMetrics?.totalVehicles || 0}
                            </p>
                        </div>
                        <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
                            <TruckIcon className="h-6 w-6 text-blue-600" />
                        </div>
                    </div>
                </div>

                {/* Active Vehicles */}
                <div className="card">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-600">Active Vehicles</p>
                            <p className="text-3xl font-bold text-green-600 mt-2">
                                {fleetMetrics?.activeVehicles || 0}
                            </p>
                        </div>
                        <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center">
                            <TruckIcon className="h-6 w-6 text-green-600" />
                        </div>
                    </div>
                </div>

                {/* Average Utilization */}
                <div className="card">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-600">Avg Utilization</p>
                            <p className="text-3xl font-bold text-purple-600 mt-2">
                                {fleetMetrics?.averageUtilization.toFixed(1) || 0}%
                            </p>
                        </div>
                        <div className="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center">
                            <ChartBarIcon className="h-6 w-6 text-purple-600" />
                        </div>
                    </div>
                </div>

                {/* Today's Revenue */}
                <div className="card">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-600">Today's Revenue</p>
                            <p className="text-3xl font-bold text-amber-600 mt-2">
                                ₹{revenueMetrics?.todayRevenue.toLocaleString() || 0}
                            </p>
                        </div>
                        <div className="h-12 w-12 bg-amber-100 rounded-lg flex items-center justify-center">
                            <CurrencyDollarIcon className="h-6 w-6 text-amber-600" />
                        </div>
                    </div>
                </div>
            </div>

            {/* Additional Stats */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Fleet Status */}
                <div className="card">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Fleet Status</h3>
                    <div className="space-y-3">
                        <div className="flex justify-between items-center">
                            <span className="text-gray-600">Idle Vehicles</span>
                            <span className="font-semibold text-gray-900">{fleetMetrics?.idleVehicles || 0}</span>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-gray-600">In Maintenance</span>
                            <span className="font-semibold text-gray-900">{fleetMetrics?.maintenanceVehicles || 0}</span>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-gray-600">Distance Covered Today</span>
                            <span className="font-semibold text-gray-900">
                                {fleetMetrics?.totalDistanceCovered.toFixed(1) || 0} km
                            </span>
                        </div>
                    </div>
                </div>

                {/* Revenue Breakdown */}
                <div className="card">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Revenue Overview</h3>
                    <div className="space-y-3">
                        <div className="flex justify-between items-center">
                            <span className="text-gray-600">This Week</span>
                            <span className="font-semibold text-gray-900">
                                ₹{revenueMetrics?.weekRevenue.toLocaleString() || 0}
                            </span>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-gray-600">This Month</span>
                            <span className="font-semibold text-gray-900">
                                ₹{revenueMetrics?.monthRevenue.toLocaleString() || 0}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DashboardPage;
