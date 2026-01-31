import { create } from 'zustand';
import { Notification, NotificationType } from '../types';

// ==========================================
// NOTIFICATION STORE STATE
// ==========================================

interface NotificationState {
    notifications: Notification[];
    unreadCount: number;
}

interface NotificationActions {
    addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
    markAsRead: (id: string) => void;
    markAllAsRead: () => void;
    removeNotification: (id: string) => void;
    clearAll: () => void;
    showToast: (type: NotificationType, title: string, message: string) => void;
}

type NotificationStore = NotificationState & NotificationActions;

// ==========================================
// ZUSTAND STORE
// ==========================================

export const useNotificationStore = create<NotificationStore>((set, get) => ({
    // Initial State
    notifications: [],
    unreadCount: 0,

    // Actions
    addNotification: (notification) => {
        const newNotification: Notification = {
            id: `notif-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            ...notification,
            timestamp: new Date().toISOString(),
            read: false,
        };

        set((state) => ({
            notifications: [newNotification, ...state.notifications],
            unreadCount: state.unreadCount + 1,
        }));
    },

    markAsRead: (id) => {
        set((state) => {
            const notification = state.notifications.find((n) => n.id === id);
            if (!notification || notification.read) return state;

            return {
                notifications: state.notifications.map((n) =>
                    n.id === id ? { ...n, read: true } : n
                ),
                unreadCount: Math.max(0, state.unreadCount - 1),
            };
        });
    },

    markAllAsRead: () => {
        set((state) => ({
            notifications: state.notifications.map((n) => ({ ...n, read: true })),
            unreadCount: 0,
        }));
    },

    removeNotification: (id) => {
        set((state) => {
            const notification = state.notifications.find((n) => n.id === id);
            const wasUnread = notification && !notification.read;

            return {
                notifications: state.notifications.filter((n) => n.id !== id),
                unreadCount: wasUnread ? Math.max(0, state.unreadCount - 1) : state.unreadCount,
            };
        });
    },

    clearAll: () => {
        set({
            notifications: [],
            unreadCount: 0,
        });
    },

    showToast: (type, title, message) => {
        get().addNotification({
            type,
            title,
            message,
        });

        // Auto-dismiss success and info toasts after 5 seconds
        if (type === 'SUCCESS' || type === 'INFO') {
            setTimeout(() => {
                const currentNotifications = get().notifications;
                if (currentNotifications.length > 0) {
                    get().removeNotification(currentNotifications[0].id);
                }
            }, 5000);
        }
    },
}));
