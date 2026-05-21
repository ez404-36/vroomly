import type React from 'react';

export interface TitleProps {
  children?: React.ReactNode;
  order?: 1 | 2 | 3 | 4 | 5 | 6;
  className?: string;
  style?: React.CSSProperties;
  ta?: 'left' | 'center' | 'right';
}
