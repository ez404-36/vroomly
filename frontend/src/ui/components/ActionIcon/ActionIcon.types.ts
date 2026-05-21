import type React from 'react';

export interface ActionIconProps {
  children?: React.ReactNode;
  variant?: 'filled' | 'subtle' | 'subtleInverse' | 'ghost' | 'ghostInverse' | 'outline';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  disabled?: boolean;
  loading?: boolean;
  onClick?: React.MouseEventHandler<HTMLButtonElement>;
  type?: 'button' | 'submit' | 'reset';
  'aria-label'?: string;
  className?: string;
  style?: React.CSSProperties;
}
