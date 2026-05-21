import React, { createContext, useContext } from 'react';
import type { ComponentRegistry } from '../registry';
import { defaultComponents } from '../registry';

const UIContext = createContext<ComponentRegistry>(defaultComponents);

export interface UIProviderProps {
  components?: ComponentRegistry;
  children: React.ReactNode;
}

export const UIProvider = ({ components = defaultComponents, children }: UIProviderProps): React.ReactElement => {
  return <UIContext.Provider value={components}>{children}</UIContext.Provider>;
};

export const useUIRegistry = (): ComponentRegistry => useContext(UIContext);
