import { useEffect } from 'react';
import { useNotificationStore } from '../../store/notificationStore';
import {
    CheckCircleIcon,
    ExclamationCircleIcon,
    InformationCircleIcon,
    XCircleIcon,
    XMarkIcon,
} from '@heroicons/react/24/outline';

const NotificationToast: React.FC = () => {
    const { notifications, removeNotification } = useNotificationStore();

    // Show only the latest 3 notifications
    const visibleNotifications = notifications.slice(0, 3);

    const getIcon = (type: string) => {
        switch (type) {
            case 'SUCCESS':
                return <CheckCircleIcon className="h-6 w-6 text-green-500" />;
            case 'ERROR':
                return <XCircleIcon className="h-6 w-6 text-red-500" />;
            case 'WARNING':
                return <ExclamationCircleIcon className="h-6 w-6 text-yellow-500" />;
            default:
                return <InformationCircleIcon className="h-6 w-6 text-blue-500" />;
        }
    };

    const getBackgroundColor = (type: string) => {
        switch (type) {
            case 'SUCCESS':
                return 'bg-green-50 border-green-200';
            case 'ERROR':
                return 'bg-red-50 border-red-200';
            case 'WARNING':
                return 'bg-yellow-50 border-yellow-200';
            default:
                return 'bg-blue-50 border-blue-200';
        }
    };

    return (
        <div className="fixed top-4 right-4 z-50 space-y-3 max-w-sm">
            {visibleNotifications.map((notification) => (
                <div
                    key={notification.id}
                    className={`${getBackgroundColor(
                        notification.type
                    )} border rounded-lg shadow-lg p-4 flex items-start space-x-3 slide-in`}
                >
                    {/* Icon */}
                    <div className="flex-shrink-0">{getIcon(notification.type)}</div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-gray-900">
                            {notification.title}
                        </p>
                        <p className="text-sm text-gray-700 mt-1">{notification.message}</p>
                    </div>

                    {/* Close Button */}
                    <button
                        onClick={() => removeNotification(notification.id)}
                        className="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
                    >
                        <XMarkIcon className="h-5 w-5" />
                    </button>
                </div>
            ))}
        </div>
    );
};

export default NotificationToast;
