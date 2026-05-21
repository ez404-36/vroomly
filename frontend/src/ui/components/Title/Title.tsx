import React from 'react';
import { clsx } from 'clsx';
import { titleVariants } from './Title.styles';
import type { TitleProps } from './Title.types';

const tagMap: Record<1 | 2 | 3 | 4 | 5 | 6, 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6'> = {
  1: 'h1',
  2: 'h2',
  3: 'h3',
  4: 'h4',
  5: 'h5',
  6: 'h6',
};

export const Title = React.forwardRef<HTMLHeadingElement, TitleProps>(
  ({ children, order = 2, className, style, ta }, ref) => {
    const Tag = tagMap[order];

    return (
      <Tag
        ref={ref}
        className={clsx(titleVariants({ order }), ta && `text-${ta}`, className)}
        style={style}
      >
        {children}
      </Tag>
    );
  },
);

Title.displayName = 'Title';
