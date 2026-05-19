export interface PaperProps {
  withBorder?: boolean;
  p?: string | number;
  children: React.ReactNode;
  pos?: string;
  style?: React.CSSProperties;
  className?: string;
}
