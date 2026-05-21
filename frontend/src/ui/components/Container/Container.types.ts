import type React from 'react';

export interface ContainerProps {
  children?: React.ReactNode;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'full' | number;
  fluid?: boolean;
  py?: string;
  px?: number | string;
  my?: string;
  className?: string;
  style?: React.CSSProperties;
}
