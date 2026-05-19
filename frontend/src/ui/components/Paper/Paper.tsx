import React from 'react';
import { clsx } from 'clsx';
import { paperVariants } from './Paper.styles';
import type { PaperProps } from './Paper.types';

export const Paper = React.forwardRef<HTMLDivElement, PaperProps>(
  ({ children, shadow, withBorder = false, p, radius, className, style }, ref) => {
    return (
      <div
        ref={ref}
        className={clsx(paperVariants({ shadow, withBorder, radius }), className)}
        style={{ padding: p, ...style }}
      >
        {children}
      </div>
    );
  },
);

Paper.displayName = 'Paper';
