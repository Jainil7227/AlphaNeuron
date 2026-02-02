import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
  glass?: boolean;
}

export function Card({ children, className = '', hover = false, glass = false }: CardProps) {
  const baseStyles = glass
    ? 'backdrop-blur-md bg-white/80 border border-white/20'
    : 'bg-white shadow-sm border border-gray-100';

  const hoverStyles = hover ? 'hover:-translate-y-1 transition-transform cursor-pointer' : '';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`rounded-xl p-6 ${baseStyles} ${hoverStyles} ${className}`}
    >
      {children}
    </motion.div>
  );
}
