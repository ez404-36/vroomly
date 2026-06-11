import React from 'react';
import { clsx } from 'clsx';
import { textVariants } from './Text.styles';
import type { TextProps } from './Text.types';

export const Text = React.forwardRef<HTMLElement, TextProps>(
  ({ children, as: Tag = 'p', size, color, c, fw, ta, mt, className, style, ...rest }, ref) => {
    const resolvedColor = c === 'red' ? 'red' : c === 'dimmed' ? 'dimmed' : c === 'primary' ? 'primary' : color;
    const fwStr = typeof fw === 'number' ? undefined : fw;

    return (
      <Tag
        ref={ref as React.Ref<HTMLElement>}
        className={clsx(
          textVariants({ size, color: resolvedColor as TextProps['color'], fw: fwStr }),
          ta && `text-${ta}`,
          className,
        )}
        style={{ marginTop: mt, ...style }}
        {...rest}
      >
        {children}
      </Tag>
    );
  },
);

Text.displayName = 'Text';
