import { NavLink } from 'react-router-dom';
import {
    HomeIcon,
    TruckIcon,
    CubeIcon,
    MapIcon,
    ChartBarIcon,
} from '@heroicons/react/24/outline';

const Sidebar: React.FC = () => {
    const navItems = [
        { name: 'Dashboard', path: '/dashboard', icon: HomeIcon },
        { name: 'Vehicles', path: '/vehicles', icon: TruckIcon },
        { name: 'Loads', path: '/loads', icon: CubeIcon },
        { name: 'Routes', path: '/routes', icon: MapIcon },
        { name: 'Analytics', path: '/analytics', icon: ChartBarIcon },
    ];

    return (
        <aside className="w-64 bg-white shadow-lg flex flex-col">
            {/* Logo */}
            <div className="h-16 flex items-center justify-center border-b border-gray-200">
                <h1 className="text-2xl font-bold text-primary-600">
                    Neuro<span className="text-gray-800">Logistics</span>
                </h1>
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-4 py-6 space-y-2">
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) =>
                            `flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors duration-200 ${isActive
                                ? 'bg-primary-50 text-primary-600 font-medium'
                                : 'text-gray-700 hover:bg-gray-100'
                            }`
                        }
                    >
                        <item.icon className="h-6 w-6" />
                        <span>{item.name}</span>
                    </NavLink>
                ))}
            </nav>

            {/* Footer */}
            <div className="p-4 border-t border-gray-200">
                <p className="text-xs text-gray-500 text-center">
                    © 2026 NeuroLogistics
                </p>
            </div>
        </aside>
    );
};

export default Sidebar;
