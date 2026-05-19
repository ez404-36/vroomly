import { DatePickerInput as MantineDatePickerInputBase } from '@mantine/dates';
import type { DatePickerInputProps } from './types';

export const MantineDatePickerInput = (props: DatePickerInputProps) => {
  const { label, placeholder = 'Выберите дату', value, onChange, error, disabled, required, clearable, ...rest } = props;

  return (
    <MantineDatePickerInputBase
      label={label}
      placeholder={placeholder}
      valueFormat="DD-MM-YYYY"
      value={value}
      onChange={onChange as (value: Date | null) => void}
      error={error}
      disabled={disabled}
      required={required}
      clearable={clearable}
      popoverProps={{ position: 'top' }}
      {...rest}
    />
  );
};
