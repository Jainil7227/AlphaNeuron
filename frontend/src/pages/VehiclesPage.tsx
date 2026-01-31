import { useEffect } from 'react';
import { useVehicleStore } from '../store/vehicleStore';
import { STATUS_COLORS } from '../utils/constants';
import { formatEnumValue } from '../utils/formatters';
import { TruckIcon } from '@heroicons/react/24/outline';

const VehiclesPage: React.FC = () => {
    const { vehicles, isLoading, fetchVehicles, selectVehicle } = useVehicleStore();

    useEffect(() => {
        fetchVehicles();
    }, [fetchVehicles]);

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
                    <h1 className="text-3xl font-bold text-gray-900">Vehicles</h1>
                    <p className="text-gray-600 mt-1">Manage your fleet of vehicles</p>
                </div>
                <button className="btn-primary">
                    Add Vehicle
                </button>
            </div>

            {/* Vehicles Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {vehicles.map((vehicle) => (
                    <div
                        key={vehicle.id}
                        className="card hover:shadow-lg transition-shadow cursor-pointer"
                        onClick={() => selectVehicle(vehicle)}
                    >
                        {/* Vehicle Header */}
                        <div className="flex items-start justify-between mb-4">
                            <div className="flex items-center space-x-3">
                                <div className="h-12 w-12 bg-primary-100 rounded-lg flex items-center justify-center">
                                    <TruckIcon className="h-6 w-6 text-primary-600" />
                                </div>
                                <div>
                                    <h3 className="font-semibold text-gray-900">{vehicle.registrationNumber}</h3>
                                    <p className="text-sm text-gray-600">{formatEnumValue(vehicle.type)}</p>
                                </div>
                            </div>
                        </div>

                        {/* Status Badge */}
                        <div className="mb-4">
                            <span
                                className="badge text-white"
                                style={{ backgroundColor: STATUS_COLORS.VEHICLE[vehicle.status] }}
                            >
                                {formatEnumValue(vehicle.status)}
                            </span>
                        </div>

                        {/* Vehicle Details */}
                        <div className="space-y-2 text-sm">
                            <div className="flex justify-between">
                                <span className="text-gray-600">Driver</span>
                                <span className="font-medium text-gray-900">{vehicle.driverName}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">Capacity</span>
                                <span className="font-medium text-gray-900">
                                    {vehicle.capacity.maxWeight} kg
                                </span>
                            </div>
                            {vehicle.currentLoadPercentage > 0 && (
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Load %</span>
                                    <span className="font-medium text-gray-900">{vehicle.currentLoadPercentage}%</span>
                                </div>
                            )}
                        </div>

                        {/* Utilization Bar */}
                        <div className="mt-4">
                            <div className="flex justify-between text-xs text-gray-600 mb-1">
                                <span>Utilization</span>
                                <span>{vehicle.currentLoadPercentage}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                                <div
                                    className="bg-primary-600 h-2 rounded-full"
                                    style={{
                                        width: `${vehicle.currentLoadPercentage}%`,
                                    }}
                                ></div>
                            </div>
                        </div>

                    </div>
                ))}
            </div>

            {/* Empty State */}
            {vehicles.length === 0 && (
                <div className="text-center py-12">
                    <TruckIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No vehicles found</h3>
                    <p className="text-gray-600">Get started by adding your first vehicle.</p>
                </div>
            )}
        </div>
    );
};

export default VehiclesPage;
