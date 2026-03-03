import type { CSSVariablesResolver } from '@mantine/core';
import { lightTokens, darkTokens } from './tokens';

export const resolver: CSSVariablesResolver = () => ({
  variables: {},

  light: {
    '--mantine-color-body': lightTokens.bgPrimary,
    '--bg-primary': lightTokens.bgPrimary,
    '--bg-secondary': lightTokens.bgSecondary,
    '--text-primary': lightTokens.textPrimary,
    '--surface': lightTokens.surface,
  },

  dark: {
    '--mantine-color-body': darkTokens.bgPrimary,
    '--bg-primary': darkTokens.bgPrimary,
    '--bg-secondary': darkTokens.bgSecondary,
    '--text-primary': darkTokens.textPrimary,
    '--surface': darkTokens.surface,
  },
});
