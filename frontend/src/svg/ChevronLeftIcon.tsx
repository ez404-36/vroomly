import { type FC, type SVGProps } from 'react';
import ChevronLeftIconRaw from './ChevronLeftIcon.svg?react';

interface ChevronLeftIconProps extends SVGProps<SVGSVGElement> {
  flipped: boolean;
}

export const ChevronLeftIcon: FC<ChevronLeftIconProps> = ({ flipped, ...props }) => (
  <ChevronLeftIconRaw
    {...props}
    style={{
      transition: 'transform 0.25s ease',
      transform: flipped ? 'rotate(180deg)' : undefined,
      ...props.style,
    }}
  />
);