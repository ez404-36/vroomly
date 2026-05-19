import { Flex as MantineFlexBase } from '@mantine/core';
import type { FlexProps } from './types';

export const MantineFlex = (props: FlexProps) => {
  const { gap = 'sm', direction, justify, children, mt, ...rest } = props;

  return (
    <MantineFlexBase gap={gap} direction={direction} justify={justify} mt={mt} {...rest}>
      {children}
    </MantineFlexBase>
  );
};
