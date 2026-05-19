import type React from 'react';

export interface StackProps {
  children?: React.ReactNode;
  gap?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | number;
  align?: 'start' | 'center' | 'end' | 'stretch';
  justify?: 'start' | 'center' | 'end' | 'between' | 'around';
  className?: string;
  style?: React.CSSProperties;
  h?: string | number;
  p?: string;
}
