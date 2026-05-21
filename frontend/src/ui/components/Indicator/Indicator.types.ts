import type React from 'react';

export interface IndicatorProps {
  children: React.ReactNode;
  color?: string;
  size?: number;
  offset?: number;
  processing?: boolean;
  disabled?: boolean;
  className?: string;
}
