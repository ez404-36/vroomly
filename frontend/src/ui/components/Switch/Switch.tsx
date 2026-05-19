import React from 'react';
import { clsx } from 'clsx';
import {
  switchTrack,
  switchTrackChecked,
  switchTrackUnchecked,
  switchThumb,
  switchThumbChecked,
} from './Switch.styles';
import type { SwitchProps } from './Switch.types';

export const Switch = React.forwardRef<HTMLInputElement, SwitchProps>(
  (
    {
      label,
      checked,
      onChange,
      onCheckedChange,
      disabled = false,
      className,
      ...rest
    },
    ref,
  ) => {
    const isChecked = checked ?? false;

    const handleChange: React.ChangeEventHandler<HTMLInputElement> = (e) => {
      onChange?.(e);
      onCheckedChange?.(e.target.checked);
    };

    return (
      <label
        className={clsx(
          'flex items-center gap-2 cursor-pointer select-none',
          disabled && 'opacity-50 cursor-not-allowed',
          className,
        )}
      >
        <input
          ref={ref}
          type="checkbox"
          checked={isChecked}
          onChange={handleChange}
          disabled={disabled}
          className="sr-only"
          {...rest}
        />
        <span
          className={clsx(
            switchTrack,
            isChecked ? switchTrackChecked : switchTrackUnchecked,
          )}
        >
          <span
            className={clsx(switchThumb, isChecked && switchThumbChecked)}
          />
        </span>
        {label && <span className="text-sm text-(--color-text)">{label}</span>}
      </label>
    );
  },
);

Switch.displayName = 'Switch';
