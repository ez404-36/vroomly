import type React from 'react';

export interface TextProps {
  children?: React.ReactNode;
  as?: 'p' | 'span' | 'div' | 'label';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  color?: 'default' | 'muted' | 'red' | 'primary' | 'dimmed';
  /** Alias for color, some call sites use `c` (Mantine compat) */
  c?: 'red' | 'dimmed' | 'primary';
  fw?: 'normal' | 'medium' | 'semibold' | 'bold' | number;
  ta?: 'left' | 'center' | 'right';
  mt?: string;
  className?: string;
  style?: React.CSSProperties;
}
