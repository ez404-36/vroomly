export interface ActionIconProps {
  children?: React.ReactNode;
  variant?: 'filled' | 'outline' | 'subtle' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  onClick?: () => void;
  'aria-label'?: string;
  className?: string;
}
