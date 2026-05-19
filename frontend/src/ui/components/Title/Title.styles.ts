import { cva } from 'class-variance-authority';

export const titleVariants = cva('font-bold leading-tight text-(--color-text)', {
  variants: {
    order: {
      1: 'text-5xl',
      2: 'text-4xl',
      3: 'text-3xl',
      4: 'text-2xl',
      5: 'text-xl',
      6: 'text-base',
    },
  },
  defaultVariants: {
    order: 2,
  },
});
