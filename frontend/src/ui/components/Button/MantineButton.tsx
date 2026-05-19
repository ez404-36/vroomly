import { Button as MantineButtonComponent } from '@mantine/core';
import type { ButtonProps } from './types';

export const MantineButton = (props: ButtonProps) => {
  const {
    children,
    variant = 'filled',
    size = 'md',
    loading = false,
    disabled = false,
    type = 'button',
    onClick,
    fullWidth = false,
    leftSection,
    rightSection,
    ...rest
  } = props;

  return (
    <MantineButtonComponent
      variant={variant}
      size={size}
      loading={loading}
      disabled={disabled}
      type={type}
      onClick={onClick}
      fullWidth={fullWidth}
      leftSection={leftSection}
      rightSection={rightSection}
      {...rest}
    >
      {children}
    </MantineButtonComponent>
  );
};