import { Load, Vehicle } from '../types';

export const calculateLoadMetrics = (loads: Load[]) => {
    const total = loads.length;
    const pending = loads.filter((l) => l.status === 'PENDING').length;
    const assigned = loads.filter((l) => l.status === 'ASSIGNED').length;
    const inTransit = loads.filter((l) => l.status === 'IN_TRANSIT').length;
    const delivered = loads.filter((l) => l.status === 'DELIVERED').length;

    return {
        total,
        pending,
        assigned,
        inTransit,
        delivered,
        deliveryRate: total > 0 ? ((delivered / total) * 100).toFixed(1) : '0',
    };
};

export const calculateVehicleMetrics = (vehicles: Vehicle[]) => {
    const total = vehicles.length;
    const available = vehicles.filter((v) => v.status === 'AVAILABLE').length;
    const inTransit = vehicles.filter((v) => v.status === 'IN_TRANSIT').length;
    const maintenance = vehicles.filter((v) => v.status === 'MAINTENANCE').length;

    return {
        total,
        available,
        inTransit,
        maintenance,
        utilizationRate: total > 0 ? (((inTransit / total) * 100).toFixed(1)) : '0',
    };
};

export const calculateRevenueMetrics = (loads: Load[]) => {
    const deliveredLoads = loads.filter((l) => l.status === 'DELIVERED');
    const totalRevenue = deliveredLoads.reduce((sum, load) => sum + load.cost, 0);
    const averageRevenue = deliveredLoads.length > 0
        ? totalRevenue / deliveredLoads.length
        : 0;

    return {
        totalRevenue: totalRevenue.toFixed(2),
        averageRevenue: averageRevenue.toFixed(2),
        deliveredCount: deliveredLoads.length,
    };
};

export const getUpcomingDeliveries = (loads: Load[], days: number = 7) => {
    const now = new Date();
    const futureDate = new Date(now.getTime() + days * 24 * 60 * 60 * 1000);

    return loads.filter((load) => {
        if (!load.deliveryDate) return false;
        const deliveryDate = new Date(load.deliveryDate);
        return deliveryDate >= now && deliveryDate <= futureDate;
    });
};
