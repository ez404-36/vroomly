import { colors } from '../tokens/colors';

export const lightTheme = {
  '--color-primary': colors.primary,
  '--color-primary-hover': colors.primaryHover,
  '--color-primary-fg': colors.primaryFg,
  '--color-primary-subtle': colors.primarySubtle,
  '--color-secondary': 'transparent',
  '--color-secondary-fg': colors.textLight,
  '--color-ghost-hover': colors.ghostHoverLight,
  '--color-danger': colors.danger,
  '--color-danger-hover': colors.dangerHover,
  '--color-danger-fg': colors.dangerFg,
  '--color-text': colors.textLight,
  '--color-text-muted': colors.textMutedLight,
  '--color-border': colors.borderLight,
  '--color-surface': colors.surfaceLight,
  '--color-bg': colors.bgLight,
  '--color-bg-muted': colors.bgMutedLight,
  '--color-input-bg': colors.inputBgLight,
  '--ring': colors.primary,
} as const;
