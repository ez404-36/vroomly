import type React from 'react';

export interface FlexProps {
  children?: React.ReactNode;
  direction?: 'row' | 'column' | 'row-reverse' | 'column-reverse';
  align?: 'start' | 'center' | 'end' | 'stretch' | 'baseline';
  justify?: 'start' | 'center' | 'end' | 'between' | 'around' | 'evenly';
  gap?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | number;
  wrap?: 'wrap' | 'nowrap' | 'wrap-reverse';
  className?: string;
  style?: React.CSSProperties;
  mt?: string;
}
