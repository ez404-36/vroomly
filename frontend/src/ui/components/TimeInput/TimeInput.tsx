import React from 'react';
import { clsx } from 'clsx';
import { inputBase, inputError, labelBase, errorBase } from '../TextInput/TextInput.styles';
import type { TimeInputProps } from './TimeInput.types';

export const TimeInput = React.forwardRef<HTMLInputElement, TimeInputProps>(
  ({ label, error, mt, wrapperClassName, className, value, onChange, placeholder = 'Выберите время', disabled = false, required }, ref) => {
    const handleChange: React.ChangeEventHandler<HTMLInputElement> = (e) => {
      onChange?.(e.target.value || null);
    };

    return (
      <div className={clsx('flex flex-col', wrapperClassName)} style={{ marginTop: mt }}>
        {label && (
          <label className={labelBase}>
            {label}
            {required && <span className="text-(--color-danger) ml-0.5">*</span>}
          </label>
        )}
        <input
          ref={ref}
          type="time"
          value={value ?? ''}
          onChange={handleChange}
          placeholder={placeholder}
          disabled={disabled}
          className={clsx(inputBase, error && inputError, className)}
        />
        {error && <span className={errorBase}>{error}</span>}
      </div>
    );
  },
);

TimeInput.displayName = 'TimeInput';