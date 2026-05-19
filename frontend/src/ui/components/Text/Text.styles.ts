import { cva } from 'class-variance-authority';

export const textVariants = cva('', {
  variants: {
    size: {
      xs: 'text-xs',
      sm: 'text-sm',
      md: 'text-base',
      lg: 'text-lg',
      xl: 'text-xl',
    },
    color: {
      default: 'text-(--color-text)',
      muted: 'text-(--color-text-muted)',
      dimmed: 'text-(--color-text-muted)',
      red: 'text-(--color-danger)',
      primary: 'text-(--color-primary)',
    },
    fw: {
      normal: 'font-normal',
      medium: 'font-medium',
      semibold: 'font-semibold',
      bold: 'font-bold',
    },
  },
  defaultVariants: {
    size: 'md',
    color: 'default',
    fw: 'normal',
  },
});
