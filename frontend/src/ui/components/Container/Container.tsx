import React from 'react';
import { clsx } from 'clsx';
import { containerVariants } from './Container.styles';
import type { ContainerProps } from './Container.types';

export const Container = React.forwardRef<HTMLDivElement, ContainerProps>(
  ({ children, size, fluid = false, py, px, my, className, style }, ref) => {
    const sizeKey =
      fluid || size === undefined
        ? 'full'
        : typeof size === 'number'
          ? undefined
          : (size as 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'full');

    const inlineStyle: React.CSSProperties = {
      ...(typeof size === 'number' ? { maxWidth: `${size}px` } : {}),
      ...(py !== undefined ? { paddingTop: py, paddingBottom: py } : {}),
      ...(px !== undefined ? { paddingLeft: px, paddingRight: px } : {}),
      ...(my !== undefined ? { marginTop: my, marginBottom: my } : {}),
      ...style,
    };

    return (
      <div
        ref={ref}
        className={clsx(containerVariants({ size: sizeKey }), className)}
        style={inlineStyle}
      >
        {children}
      </div>
    );
  },
);

Container.displayName = 'Container';
