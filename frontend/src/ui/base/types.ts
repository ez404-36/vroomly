import type { UIProvider } from '../config/provider';

export type { UIProvider };

export interface BaseProps {
  className?: string;
  'data-testid'?: string;
  onClick?: () => void;
}