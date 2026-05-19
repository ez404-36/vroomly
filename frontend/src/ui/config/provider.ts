export type UIProvider = 'mantine' | 'mui' | 'chakra' | 'shadcn';

export interface UIConfig {
  provider: UIProvider;
  theme?: {
    primaryColor?: string;
  };
}

export const uiConfig: UIConfig = {
  provider: 'mantine',
};