import { VehicleStatus, LoadStatus } from '../../types';
import { STATUS_COLORS } from '../../utils/constants';
import { formatEnumValue } from '../../utils/formatters';

interface StatusBadgeProps {
    status: VehicleStatus | LoadStatus;
    type: 'vehicle' | 'load';
    size?: 'sm' | 'md' | 'lg';
}

const StatusBadge: React.FC<StatusBadgeProps> = ({
    status,
    type,
    size = 'md',
}) => {
    const sizeClasses = {
        sm: 'text-xs px-2 py-0.5',
        md: 'text-sm px-3 py-1',
        lg: 'text-base px-4 py-1.5',
    };

    const colorMap = type === 'vehicle' ? STATUS_COLORS.VEHICLE : STATUS_COLORS.LOAD;
    const backgroundColor = colorMap[status as keyof typeof colorMap];

    return (
        <span
            className={`inline-flex items-center rounded-full font-medium text-white ${sizeClasses[size]}`}
            style={{ backgroundColor }}
        >
            {formatEnumValue(status)}
        </span>
    );
};

export default StatusBadge;
