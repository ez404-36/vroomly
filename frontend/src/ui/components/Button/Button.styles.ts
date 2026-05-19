import { cva } from 'class-variance-authority';

export const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[--ring] disabled:opacity-50 disabled:pointer-events-none cursor-pointer',
  {
    variants: {
      variant: {
        filled: 'bg-[--color-primary] text-[--color-primary-fg] hover:bg-[--color-primary-hover]',
        primary: 'bg-[--color-primary] text-[--color-primary-fg] hover:bg-[--color-primary-hover]',
        outline: 'border border-[--color-primary] text-[--color-primary] bg-transparent hover:bg-[--color-primary-subtle]',
        secondary: 'border border-[--color-primary] text-[--color-primary] bg-transparent hover:bg-[--color-primary-subtle]',
        subtle: 'bg-transparent text-[--color-text] hover:bg-[--color-ghost-hover]',
        ghost: 'bg-transparent text-[--color-text] hover:bg-[--color-ghost-hover]',
        danger: 'bg-[--color-danger] text-[--color-danger-fg] hover:bg-[--color-danger-hover]',
      },
      size: {
        xs: 'h-6 px-2 text-xs',
        sm: 'h-8 px-3 text-sm',
        md: 'h-9 px-4 text-sm',
        lg: 'h-11 px-6 text-base',
      },
      fullWidth: {
        true: 'w-full',
        false: '',
      },
    },
    defaultVariants: {
      variant: 'filled',
      size: 'md',
      fullWidth: false,
    },
  },
);
