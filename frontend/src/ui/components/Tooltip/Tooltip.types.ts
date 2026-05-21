import type React from 'react';

export interface TooltipProps {
  children: React.ReactElement;
  label: React.ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
  disabled?: boolean;
  className?: string;
}
