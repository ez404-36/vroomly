export interface FlexProps {
  gap?: 'xs' | 'sm' | 'md' | 'lg';
  direction?: 'row' | 'column';
  justify?: 'start' | 'center' | 'end' | 'between';
  children: React.ReactNode;
  mt?: string;
  className?: string;
}
