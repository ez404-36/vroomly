import React from 'react';
import { clsx } from 'clsx';
import { switchTrack, switchTrackChecked, switchThumb, switchThumbChecked } from './Switch.styles';
import type { SwitchProps } from './Switch.types';

export const Switch = React.forwardRef<HTMLInputElement, SwitchProps>(
  ({ label, checked, onChange, onCheckedChange, disabled = false, className, ...rest }, ref) => {
    const handleChange: React.ChangeEventHandler<HTMLInputElement> = (e) => {
      onChange?.(e);
      onCheckedChange?.(e.target.checked);
    };

    return (
      <label className={clsx('flex items-center gap-2 cursor-pointer', disabled && 'opacity-50 cursor-not-allowed', className)}>
        <div className={clsx(switchTrack, checked && switchTrackChecked)}>
          <span className={clsx(switchThumb, checked && switchThumbChecked)} />
        </div>
        <input
          ref={ref}
          type="checkbox"
          checked={checked}
          onChange={handleChange}
          disabled={disabled}
          className="sr-only"
          {...rest}
        />
        {label && <span className="text-sm text-[--color-text]">{label}</span>}
      </label>
    );
  },
);

Switch.displayName = 'Switch';
