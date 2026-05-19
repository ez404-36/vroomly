import React from 'react';
import { clsx } from 'clsx';
import { flexVariants } from './Flex.styles';
import type { FlexProps } from './Flex.types';

export const Flex = React.forwardRef<HTMLDivElement, FlexProps>(
  ({ children, direction, align, justify, gap, wrap, className, style, mt }, ref) => {
    const gapKey = typeof gap === 'string' ? (gap as 'xs' | 'sm' | 'md' | 'lg' | 'xl') : undefined;
    const gapStyle = typeof gap === 'number' ? { gap: `${gap}px` } : undefined;

    return (
      <div
        ref={ref}
        className={clsx(flexVariants({ direction, align, justify, gap: gapKey, wrap }), className)}
        style={{ ...gapStyle, marginTop: mt, ...style }}
      >
        {children}
      </div>
    );
  },
);

Flex.displayName = 'Flex';
