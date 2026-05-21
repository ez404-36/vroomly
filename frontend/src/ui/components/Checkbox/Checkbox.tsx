import React from 'react';
import { clsx } from 'clsx';
import {
  checkboxControl,
  checkboxIcon,
  checkboxWrapper,
  checkboxWrapperDisabled,
} from './Checkbox.styles';
import type { CheckboxProps } from './Checkbox.types';

export const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(
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
          checkboxWrapper,
          disabled && checkboxWrapperDisabled,
          className,
        )}
      >
        <div className="relative">
          <input
            ref={ref}
            type="checkbox"
            checked={isChecked}
            onChange={handleChange}
            disabled={disabled}
            className="sr-only"
            {...rest}
          />
          <div
            className={clsx(
              checkboxControl,
              'grid place-items-center',
            )}
          >
            {isChecked && (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="4"
                strokeLinecap="round"
                strokeLinejoin="round"
                className={checkboxIcon}
              >
                <polyline points="20 6 9 17 4 12" />
              </svg>
            )}
          </div>
        </div>
        {label && <span className="text-sm text-(--color-text)">{label}</span>}
      </label>
    );
  },
);

Checkbox.displayName = 'Checkbox';