import { Text as MantineTextBase } from '@mantine/core';
import type { TextProps } from './types';

const colorMap: Record<string, string | undefined> = {
  red: 'red',
  blue: 'blue',
  gray: 'gray',
  primary: 'orange',
  dimmed: 'dimmed',
};

export const MantineText = (props: TextProps) => {
  const { children, size = 'sm', color, fw, mt, ...rest } = props;

  return (
    <MantineTextBase
      size={size}
      c={color ? colorMap[color] : undefined}
      fw={fw}
      mt={mt}
      {...rest}
    >
      {children}
    </MantineTextBase>
  );
};
