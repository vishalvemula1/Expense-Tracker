import { ReactNode } from 'react';
import { motion } from 'framer-motion';

interface CardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
}

export function Card({ children, className = '', hover = false }: CardProps) {
  const Component = hover ? motion.div : 'div';

  return (
    <Component
      {...(hover && {
        whileHover: { y: -2, shadow: 'lg' },
        transition: { duration: 0.2 },
      })}
      className={`card ${className}`}
    >
      {children}
    </Component>
  );
}
