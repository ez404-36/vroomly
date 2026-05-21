import { colors } from '../tokens/colors';

export const darkTheme = {
  '--color-primary': colors.primaryDark,
  '--color-primary-hover': colors.primaryDarkHover,
  '--color-primary-fg': colors.primaryFg,
  '--color-primary-subtle': 'rgba(255, 115, 0, 0.15)',
  '--color-secondary': 'transparent',
  '--color-secondary-fg': colors.textDark,
  '--color-ghost-hover': colors.ghostHoverDark,
  '--color-danger': colors.danger,
  '--color-danger-hover': colors.dangerHover,
  '--color-danger-fg': colors.dangerFg,
  '--color-text': colors.textDark,
  '--color-text-muted': colors.textMutedDark,
  '--color-border': colors.borderDark,
  '--color-surface': colors.surfaceDark,
  '--color-bg': colors.bgDark,
  '--color-bg-muted': colors.bgMutedDark,
  '--color-input-bg': colors.inputBgDark,
  '--ring': colors.primaryDark,
} as const;
