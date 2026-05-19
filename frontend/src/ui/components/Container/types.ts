export interface ContainerProps {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'full';
  children: React.ReactNode;
  className?: string;
}
