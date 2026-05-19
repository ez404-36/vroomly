import React from 'react';
import { clsx } from 'clsx';
import { buttonVariants } from './Button.styles';
import type { ButtonProps } from './Button.types';

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      variant = 'filled',
      size = 'md',
      disabled = false,
      loading = false,
      type = 'button',
      onClick,
      fullWidth = false,
      leftSection,
      rightSection,
      mt,
      className,
      style,
      ...rest
    },
    ref,
  ) => {
    return (
      <button
        ref={ref}
        type={type}
        disabled={disabled || loading}
        onClick={onClick}
        className={clsx(buttonVariants({ variant, size, fullWidth }), className)}
        style={{ marginTop: mt, ...style }}
        {...rest}
      >
        {loading && (
          <svg
            className="animate-spin h-4 w-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
        )}
        {!loading && leftSection}
        {children}
        {rightSection}
      </button>
    );
  },
);

Button.displayName = 'Button';
