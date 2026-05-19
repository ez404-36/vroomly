import { ActionIcon as MantineActionIconBase } from '@mantine/core';
import type { ActionIconProps } from './types';

export const MantineActionIcon = (props: ActionIconProps) => {
  const { children, variant = 'subtle', size = 'md', disabled, onClick, ...rest } = props;

  return (
    <MantineActionIconBase
      variant={variant}
      size={size}
      disabled={disabled}
      onClick={onClick}
      {...rest}
    >
      {children}
    </MantineActionIconBase>
  );
};
