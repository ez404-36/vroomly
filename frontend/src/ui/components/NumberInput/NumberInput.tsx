import React from 'react';
import { clsx } from 'clsx';
import { inputBase, inputError, labelBase, errorBase } from '../TextInput/TextInput.styles';
import type { NumberInputProps } from './NumberInput.types';

export const NumberInput = React.forwardRef<HTMLInputElement, NumberInputProps>(
  ({ label, error, mt, wrapperClassName, className, decimalScale, onValueChange, onChange, ...rest }, ref) => {
    const handleChange: React.ChangeEventHandler<HTMLInputElement> = (e) => {
      onChange?.(e);
      if (onValueChange) {
        const parsed = e.target.value !== '' ? Number(e.target.value) : undefined;
        onValueChange(parsed);
      }
    };

    return (
      <div className={clsx('flex flex-col', wrapperClassName)} style={{ marginTop: mt }}>
        {label && <label className={labelBase}>{label}</label>}
        <input
          ref={ref}
          type="number"
          step={decimalScale !== undefined ? Math.pow(10, -decimalScale) : undefined}
          className={clsx(inputBase, error && inputError, className)}
          onChange={handleChange}
          {...rest}
        />
        {error && <span className={errorBase}>{error}</span>}
      </div>
    );
  },
);

NumberInput.displayName = 'NumberInput';
