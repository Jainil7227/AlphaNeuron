import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

interface ProtectedRouteProps {
    children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
    const { isAuthenticated, isLoading } = useAuthStore();

    if (isLoading) {
        return (
            <div className="flex h-screen items-center justify-center">
                <div className="h-16 w-16 animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent motion-reduce:animate-[spin_1.5s_linear_infinite]" />
            </div>
        );
    }

    if (!isAuthenticated) {
        // While checkAuth is running (which now does auto-login), we might be here briefly.
        // We show loading instead of redirecting.
        return (
            <div className="flex h-screen items-center justify-center">
                <div className="h-16 w-16 animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent motion-reduce:animate-[spin_1.5s_linear_infinite]" />
            </div>
        );
    }

    return <>{children}</>;
};

export default ProtectedRoute;
