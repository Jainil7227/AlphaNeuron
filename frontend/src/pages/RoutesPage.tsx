import { useEffect, useState } from 'react';
import { routeApi } from '../api';
import { Route } from '../types';
import { formatDateTime, formatDistance } from '../utils/formatters';
import { MapIcon, ClockIcon, TruckIcon } from '@heroicons/react/24/outline';

const RoutesPage: React.FC = () => {
    const [routes, setRoutes] = useState<Route[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchRoutes = async () => {
            try {
                const data = await routeApi.getAll();
                setRoutes(data);
            } catch (error) {
                console.error('Failed to fetch routes:', error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchRoutes();
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
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Routes</h1>
                    <p className="text-gray-600 mt-1">Optimized delivery routes</p>
                </div>
                <button className="btn-primary">
                    Optimize Routes
                </button>
            </div>

            {/* Routes List */}
            <div className="space-y-4">
                {routes.map((route) => (
                    <div key={route.id} className="card hover:shadow-lg transition-shadow">
                        {/* Route Header */}
                        <div className="flex items-start justify-between mb-4">
                            <div className="flex items-center space-x-3">
                                <div className="h-12 w-12 bg-indigo-100 rounded-lg flex items-center justify-center">
                                    <MapIcon className="h-6 w-6 text-indigo-600" />
                                </div>
                                <div>
                                    <h3 className="font-semibold text-gray-900">Route #{route.id}</h3>
                                    <p className="text-sm text-gray-600">
                                        {route.waypoints.length} stops • {formatDistance(route.totalDistance)}
                                    </p>
                                </div>
                            </div>
                            <div className="text-right">
                                <p className="text-sm text-gray-600">ETA</p>
                                <p className="font-semibold text-gray-900">{route.estimatedDuration} min</p>
                            </div>
                        </div>

                        {/* Vehicle Info */}
                        <div className="flex items-center space-x-2 mb-4 p-3 bg-gray-50 rounded-lg">
                            <TruckIcon className="h-5 w-5 text-gray-600" />
                            <span className="text-sm text-gray-700">
                                Vehicle: <span className="font-medium">{route.vehicleId}</span>
                            </span>
                        </div>

                        {/* Waypoints */}
                        <div className="space-y-2">
                            <h4 className="text-sm font-semibold text-gray-700 mb-2">Stops:</h4>
                            {route.waypoints.map((waypoint, index) => (
                                <div key={index} className="flex items-center space-x-3 p-2 hover:bg-gray-50 rounded-lg">
                                    <div className="flex-shrink-0 h-8 w-8 bg-primary-100 rounded-full flex items-center justify-center">
                                        <span className="text-sm font-semibold text-primary-600">{index + 1}</span>
                                    </div>
                                    <div className="flex-1">
                                        <p className="text-sm font-medium text-gray-900">{waypoint.address || 'Address N/A'}</p>
                                        <p className="text-xs text-gray-500">
                                            {waypoint.city || 'Unknown City'}, {waypoint.state || 'Unknown State'} - {waypoint.pincode || 'N/A'}
                                        </p>
                                    </div>
                                    <div className="text-right">
                                        <ClockIcon className="h-4 w-4 text-gray-400 inline mr-1" />
                                        <span className="text-xs text-gray-600">
                                            {formatDateTime(waypoint.estimatedArrival || new Date().toISOString())}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* Route Actions */}
                        <div className="mt-4 pt-4 border-t border-gray-200 flex space-x-2">
                            <button className="btn-secondary text-sm flex-1">
                                View Map
                            </button>
                            <button className="btn-primary text-sm flex-1">
                                Start Route
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            {/* Empty State */}
            {routes.length === 0 && (
                <div className="text-center py-12">
                    <MapIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No routes found</h3>
                    <p className="text-gray-600">Optimize your loads to generate efficient routes.</p>
                </div>
            )}
        </div>
    );
};

export default RoutesPage;
