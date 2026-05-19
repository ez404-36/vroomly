import { cva } from 'class-variance-authority';

export const actionIconVariants = cva(
  'inline-flex items-center justify-center rounded-md transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[--ring] disabled:opacity-50 disabled:pointer-events-none cursor-pointer',
  {
    variants: {
      variant: {
        filled: 'bg-[--color-primary] text-[--color-primary-fg] hover:bg-[--color-primary-hover]',
        subtle: 'bg-transparent text-[--color-text] hover:bg-[--color-ghost-hover]',
        ghost: 'bg-transparent text-[--color-text] hover:bg-[--color-ghost-hover]',
        outline: 'border border-[--color-border] text-[--color-text] bg-transparent hover:bg-[--color-ghost-hover]',
      },
      size: {
        sm: 'h-7 w-7',
        md: 'h-8 w-8',
        lg: 'h-9 w-9',
        xl: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'subtle',
      size: 'md',
    },
  },
);
