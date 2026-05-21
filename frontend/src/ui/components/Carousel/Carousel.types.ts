import type { ReactNode } from 'react';

export interface CarouselProps {
  children: ReactNode;
  className?: string;
  singleItem?: boolean;
  onIndexChange?: (index: number) => void;
  initialIndex?: number;
}