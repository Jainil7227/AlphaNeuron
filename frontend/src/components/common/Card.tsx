import { ReactNode } from 'react';

interface CardProps {
    children: ReactNode;
    title?: string;
    subtitle?: string;
    action?: ReactNode;
    padding?: 'none' | 'sm' | 'md' | 'lg';
    hover?: boolean;
    className?: string;
}

const Card: React.FC<CardProps> = ({
    children,
    title,
    subtitle,
    action,
    padding = 'md',
    hover = false,
    className = '',
}) => {
    const paddingClasses = {
        none: 'p-0',
        sm: 'p-3',
        md: 'p-6',
        lg: 'p-8',
    };

    const hoverClass = hover ? 'hover:shadow-lg transition-shadow cursor-pointer' : '';

    return (
        <div
            className={`bg-white rounded-xl shadow-md ${paddingClasses[padding]} ${hoverClass} ${className}`}
        >
            {(title || subtitle || action) && (
                <div className="flex items-start justify-between mb-4">
                    <div>
                        {title && <h3 className="text-lg font-semibold text-gray-900">{title}</h3>}
                        {subtitle && <p className="text-sm text-gray-600 mt-1">{subtitle}</p>}
                    </div>
                    {action && <div>{action}</div>}
                </div>
            )}
            {children}
        </div>
    );
};

export default Card;
