export interface TimeInputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type' | 'onChange' | 'value'> {
  label?: string;
  value?: string | null;
  onChange?: (value: string | null) => void;
  error?: string;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  className?: string;
  wrapperClassName?: string;
  mt?: number | string;
}