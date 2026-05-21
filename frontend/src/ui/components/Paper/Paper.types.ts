import type React from 'react';

export interface PaperProps {
  children?: React.ReactNode;
  shadow?: 'none' | 'sm' | 'md' | 'lg';
  withBorder?: boolean;
  p?: string;
  radius?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  style?: React.CSSProperties;
}
