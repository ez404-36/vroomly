import type React from 'react';

export interface ButtonProps {
  children?: React.ReactNode;
  variant?: 'filled' | 'primary' | 'outline' | 'secondary' | 'subtle' | 'subtleInverse' | 'ghost' | 'danger';
  size?: 'xs' | 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  onClick?: React.MouseEventHandler<HTMLButtonElement>;
  type?: 'button' | 'submit' | 'reset';
  fullWidth?: boolean;
  leftSection?: React.ReactNode;
  rightSection?: React.ReactNode;
  mt?: string;
  className?: string;
  'data-testid'?: string;
  color?: string;
  style?: React.CSSProperties;
}
