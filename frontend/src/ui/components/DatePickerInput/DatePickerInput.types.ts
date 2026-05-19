export interface DatePickerInputProps {
  label?: string;
  placeholder?: string;
  value?: Date | null;
  onChange?: (value: Date | null) => void;
  error?: string;
  disabled?: boolean;
  required?: boolean;
  clearable?: boolean;
  className?: string;
  maxDate?: Date;
  minDate?: Date;
  defaultLevel?: 'day' | 'month' | 'year' | 'decade';
}
