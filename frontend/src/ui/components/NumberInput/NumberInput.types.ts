import type React from 'react';

export interface NumberInputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'onChange'> {
  label?: string;
  error?: string;
  mt?: string;
  wrapperClassName?: string;
  decimalScale?: number;
  /** Custom numeric onChange — fires with parsed number or undefined */
  onValueChange?: (value: number | undefined) => void;
  onChange?: React.ChangeEventHandler<HTMLInputElement>;
}
