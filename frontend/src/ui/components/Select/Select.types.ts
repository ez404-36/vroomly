export interface SelectOption {
  value: string;
  label: string;
}

export interface SelectProps {
  label?: string;
  placeholder?: string;
  value?: string | null;
  onChange?: (value: string | null) => void;
  options?: SelectOption[];
  /** Alias for options (Mantine compat) */
  data?: SelectOption[];
  error?: string;
  disabled?: boolean;
  searchable?: boolean;
  clearable?: boolean;
  required?: boolean;
  className?: string;
}
