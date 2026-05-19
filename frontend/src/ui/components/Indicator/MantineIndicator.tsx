import { Indicator as MantineIndicatorBase } from '@mantine/core';
import type { IndicatorProps } from './types';

export const MantineIndicator = (props: IndicatorProps) => {
  const { children, color = 'red', size = 8, offset = 4, processing = false, ...rest } = props;

  return (
    <MantineIndicatorBase
      color={color}
      size={size}
      offset={offset}
      processing={processing}
      {...rest}
    >
      {children}
    </MantineIndicatorBase>
  );
};
