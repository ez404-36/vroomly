import { Container as MantineContainerBase } from '@mantine/core';
import type { ContainerProps } from './types';

export const MantineContainer = (props: ContainerProps) => {
  const { size = 'md', children, ...rest } = props;

  return (
    <MantineContainerBase size={size} {...rest}>
      {children}
    </MantineContainerBase>
  );
};
