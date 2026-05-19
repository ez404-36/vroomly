import type React from 'react';

export type ComponentName =
  | 'Button'
  | 'TextInput'
  | 'PasswordInput'
  | 'NumberInput'
  | 'Select'
  | 'Switch'
  | 'Container'
  | 'Paper'
  | 'Stack'
  | 'Flex'
  | 'Text'
  | 'Title'
  | 'ActionIcon'
  | 'Tooltip'
  | 'Indicator'
  | 'DatePickerInput';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type ComponentRegistry = Partial<Record<ComponentName, React.ComponentType<any>>>;

export const defaultComponents: ComponentRegistry = {};
