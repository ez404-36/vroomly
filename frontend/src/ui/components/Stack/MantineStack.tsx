import { Stack as MantineStackBase } from '@mantine/core';
import type { StackProps } from './types';

export const MantineStack = (props: StackProps) => {
  const { gap = 'md', children, ...rest } = props;

  return (
    <MantineStackBase gap={gap} {...rest}>
      {children}
    </MantineStackBase>
  );
};
