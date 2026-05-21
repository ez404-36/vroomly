import type React from 'react';
import type { ComponentName } from '../registry';
import { useUIRegistry } from './UIProvider';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function useUIComponent<T extends React.ComponentType<any>>(
  name: ComponentName,
  fallback: T,
): T {
  const registry = useUIRegistry();
  return (registry[name] as T | undefined) ?? fallback;
}
