import { Tooltip as MantineTooltipBase } from '@mantine/core';
import type { TooltipProps } from './types';

export const MantineTooltip = (props: TooltipProps) => {
  const { label, children, position = 'top', ...rest } = props;

  return (
    <MantineTooltipBase label={label} position={position} {...rest}>
      {children}
    </MantineTooltipBase>
  );
};
