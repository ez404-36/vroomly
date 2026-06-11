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

export type ComponentRegistry = Partial<Record<ComponentName, React.ComponentType<Record<string, unknown>>>>;

export const defaultComponents: ComponentRegistry = {};
