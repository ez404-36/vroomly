import { cva } from 'class-variance-authority';

export const paperVariants = cva('bg-[--color-surface]', {
  variants: {
    shadow: {
      none: '',
      sm: 'shadow-sm',
      md: 'shadow-md',
      lg: 'shadow-lg',
    },
    withBorder: {
      true: 'border border-[--color-border]',
      false: '',
    },
    radius: {
      sm: 'rounded-sm',
      md: 'rounded-md',
      lg: 'rounded-lg',
      xl: 'rounded-xl',
    },
  },
  defaultVariants: {
    shadow: 'none',
    withBorder: false,
    radius: 'md',
  },
});
