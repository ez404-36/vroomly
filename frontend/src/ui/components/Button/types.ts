export interface ButtonProps {
  children: React.ReactNode;
  variant?: 'filled' | 'outline' | 'subtle' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  fullWidth?: boolean;
  leftSection?: React.ReactNode;
  rightSection?: React.ReactNode;
  mt?: string;
  className?: string;
  'data-testid'?: string;
}