import React from 'react';
import * as RadixTooltip from '@radix-ui/react-tooltip';
import { tooltipContent } from './Tooltip.styles';
import type { TooltipProps } from './Tooltip.types';

const positionMap: Record<NonNullable<TooltipProps['position']>, RadixTooltip.TooltipContentProps['side']> = {
  top: 'top',
  bottom: 'bottom',
  left: 'left',
  right: 'right',
};

export const Tooltip = ({ children, label, position = 'top', disabled = false }: TooltipProps): React.ReactElement => {
  if (disabled) {
    return children;
  }

  return (
    <RadixTooltip.Provider delayDuration={300}>
      <RadixTooltip.Root>
        <RadixTooltip.Trigger asChild>{children}</RadixTooltip.Trigger>
        <RadixTooltip.Portal>
          <RadixTooltip.Content side={positionMap[position]} className={tooltipContent} sideOffset={4}>
            {label}
          </RadixTooltip.Content>
        </RadixTooltip.Portal>
      </RadixTooltip.Root>
    </RadixTooltip.Provider>
  );
};

Tooltip.displayName = 'Tooltip';
