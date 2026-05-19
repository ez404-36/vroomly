import { Paper as MantinePaperBase } from '@mantine/core';
import type { PaperProps } from './types';

export const MantinePaper = (props: PaperProps) => {
  const { withBorder = false, p, children, style, ...rest } = props;

  return (
    <MantinePaperBase withBorder={withBorder} p={p} style={style} {...rest}>
      {children}
    </MantinePaperBase>
  );
};
