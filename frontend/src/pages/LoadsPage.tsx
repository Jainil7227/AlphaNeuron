import { useEffect, useState } from 'react';
import { loadApi } from '../api';
import { Load } from '../types';
import { STATUS_COLORS } from '../utils/constants';
import { formatEnumValue, formatWeight, formatDateTime } from '../utils/formatters';
import { CubeIcon } from '@heroicons/react/24/outline';

const LoadsPage: React.FC = () => {
    const [loads, setLoads] = useState<Load[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [filter, setFilter] = useState<string>('ALL');

    useEffect(() => {
        const fetchLoads = async () => {
            try {
                const response = await loadApi.getAll();
                setLoads(response.data);
            } catch (error) {
                console.error('Failed to fetch loads:', error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchLoads();
    }, []);

    const filteredLoads = filter === 'ALL'
        ? loads
        : loads.filter(load => load.status === filter);

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
                    <h1 className="text-3xl font-bold text-gray-900">Loads</h1>
                    <p className="text-gray-600 mt-1">Manage shipments and deliveries</p>
                </div>
                <button className="btn-primary">
                    Create Load
                </button>
            </div>

            {/* Filter Tabs */}
            <div className="flex space-x-2 border-b border-gray-200">
                {['ALL', 'PENDING', 'IN_TRANSIT', 'DELIVERED', 'CANCELLED'].map((status) => (
                    <button
                        key={status}
                        onClick={() => setFilter(status)}
                        className={`px-4 py-2 font-medium text-sm transition-colors ${filter === status
                                ? 'text-primary-600 border-b-2 border-primary-600'
                                : 'text-gray-600 hover:text-gray-900'
                            }`}
                    >
                        {formatEnumValue(status)}
                    </button>
                ))}
            </div>

            {/* Loads Table */}
            <div className="card overflow-hidden p-0">
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-gray-50 border-b border-gray-200">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Load ID
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Origin → Destination
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Weight
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Status
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Pickup Time
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {filteredLoads.map((load) => (
                                <tr key={load.id} className="hover:bg-gray-50 cursor-pointer">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="flex items-center">
                                            <CubeIcon className="h-5 w-5 text-gray-400 mr-2" />
                                            <span className="text-sm font-medium text-gray-900">{load.id}</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="text-sm text-gray-900">{load.origin.city || load.origin.address}</div>
                                        <div className="text-sm text-gray-500">→ {load.destination.city || load.destination.address}</div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                        {formatWeight(load.weight)}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span
                                            className="badge text-white text-xs"
                                            style={{ backgroundColor: STATUS_COLORS.LOAD[load.status] }}
                                        >
                                            {formatEnumValue(load.status)}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                        {formatDateTime(load.pickupTimeWindow.start)}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Empty State */}
            {filteredLoads.length === 0 && (
                <div className="text-center py-12">
                    <CubeIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No loads found</h3>
                    <p className="text-gray-600">
                        {filter === 'ALL'
                            ? 'Get started by creating your first load.'
                            : `No loads with status: ${formatEnumValue(filter)}`}
                    </p>
                </div>
            )}
        </div>
    );
};

export default LoadsPage;
