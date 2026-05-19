import React from 'react';
import { clsx } from 'clsx';
import { stackVariants } from './Stack.styles';
import type { StackProps } from './Stack.types';

export const Stack = React.forwardRef<HTMLDivElement, StackProps>(
  ({ children, gap = 'md', align, justify, className, style, h, p }, ref) => {
    const gapKey = typeof gap === 'string' ? (gap as 'xs' | 'sm' | 'md' | 'lg' | 'xl') : undefined;
    const gapStyle = typeof gap === 'number' ? { gap: `${gap}px` } : undefined;

    const inlineStyle: React.CSSProperties = {
      ...gapStyle,
      ...(h !== undefined ? { height: typeof h === 'number' ? `${h}px` : h } : {}),
      ...(p !== undefined ? { padding: p } : {}),
      ...style,
    };

    return (
      <div
        ref={ref}
        className={clsx(stackVariants({ gap: gapKey, align, justify }), className)}
        style={inlineStyle}
      >
        {children}
      </div>
    );
  },
);

Stack.displayName = 'Stack';
