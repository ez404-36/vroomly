import React from 'react';
import { clsx } from 'clsx';
import { indicatorDotBase, indicatorProcessingPing } from './Indicator.styles';
import type { IndicatorProps } from './Indicator.types';

export const Indicator = React.forwardRef<HTMLDivElement, IndicatorProps>(
  ({ children, color = '#d20000', size = 8, offset = 0, processing = false, disabled = false, className }, ref) => {
    if (disabled) {
      return <>{children}</>;
    }

    const dotStyle: React.CSSProperties = {
      width: size,
      height: size,
      backgroundColor: color,
      top: offset,
      right: offset,
    };

    return (
      <div ref={ref} className={clsx('relative inline-flex', className)}>
        {children}
        {processing && (
          <span
            className={indicatorProcessingPing}
            style={{ ...dotStyle, backgroundColor: color }}
          />
        )}
        <span className={indicatorDotBase} style={dotStyle} />
      </div>
    );
  },
);

Indicator.displayName = 'Indicator';
