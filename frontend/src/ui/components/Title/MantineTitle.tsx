import { Title as MantineTitleBase } from '@mantine/core';
import type { TitleProps } from './types';

export const MantineTitle = (props: TitleProps) => {
  const { children, order = 2, ...rest } = props;

  return (
    <MantineTitleBase order={order} {...rest}>
      {children}
    </MantineTitleBase>
  );
};
