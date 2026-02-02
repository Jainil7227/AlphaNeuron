import { ReactNode } from 'react';

interface ButtonProps {
  children: ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'success' | 'danger' | 'warning';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  disabled?: boolean;
}

export function Button({
  children,
  onClick,
  variant = 'primary',
  size = 'md',
  className = '',
  disabled = false,
}: ButtonProps) {
  const variants = {
    primary: 'bg-neuro-blue hover:bg-blue-700 text-white',
    secondary: 'bg-neuro-slate hover:bg-slate-800 text-white',
    success: 'bg-profit-green hover:bg-green-600 text-white',
    danger: 'bg-risk-red hover:bg-red-600 text-white',
    warning: 'bg-signal-amber hover:bg-amber-600 text-white',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2',
    lg: 'px-6 py-3 text-lg',
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`rounded-lg font-medium active:scale-95 transition-all ${variants[variant]} ${sizes[size]} ${className} ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
    >
      {children}
    </button>
  );
}

