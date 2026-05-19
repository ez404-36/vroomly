export interface TextProps {
  children: React.ReactNode;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  color?: 'red' | 'blue' | 'gray' | 'primary' | 'dimmed';
  fw?: 'bold' | 'normal';
  mt?: string;
  className?: string;
}
