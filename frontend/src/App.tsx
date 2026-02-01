import { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import { useNotificationStore } from './store/notificationStore';
import websocketService from './api/websocket';

// Pages
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import VehiclesPage from './pages/VehiclesPage';
import LoadsPage from './pages/LoadsPage';
import RoutesPage from './pages/RoutesPage';
import AnalyticsPage from './pages/AnalyticsPage';
import CostCalculatorPage from './pages/CostCalculatorPage';

// Components
import ProtectedRoute from './components/auth/ProtectedRoute';
import Layout from './components/layout/Layout';
import NotificationToast from './components/notifications/NotificationToast';

function App() {
    const { checkAuth, isAuthenticated } = useAuthStore();
    const { addNotification } = useNotificationStore();

    useEffect(() => {
        // Check authentication status on mount
        checkAuth();
    }, [checkAuth]);

    useEffect(() => {
        // Setup WebSocket listeners if authenticated
        if (isAuthenticated) {
            const handleNotification = (notification: any) => {
                addNotification({
                    type: notification.type || 'INFO',
                    title: notification.title,
                    message: notification.message,
                    actionUrl: notification.actionUrl,
                });
            };

            websocketService.onNotification(handleNotification);

            return () => {
                websocketService.offNotification(handleNotification);
            };
        }
    }, [isAuthenticated, addNotification]);

    return (
        <Router>
            <div className="min-h-screen bg-gray-50">
                <Routes>

                    {/* Public Routes */}
                    <Route path="/login" element={<LoginPage />} />

                    {/* Protected Routes */}
                    <Route
                        path="/"
                        element={
                            <ProtectedRoute>
                                <Layout />
                            </ProtectedRoute>
                        }
                    >
                        <Route index element={<Navigate to="/dashboard" replace />} />
                        <Route path="dashboard" element={<DashboardPage />} />
                        <Route path="vehicles" element={<VehiclesPage />} />
                        <Route path="loads" element={<LoadsPage />} />
                        <Route path="routes" element={<RoutesPage />} />
                        <Route path="analytics" element={<AnalyticsPage />} />
                        <Route path="cost-calculator" element={<CostCalculatorPage />} />
                    </Route>

                    {/* Fallback */}
                    <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Routes>

                {/* Global Notification Toast */}
                <NotificationToast />
            </div>
        </Router>
    );
}

export default App;

