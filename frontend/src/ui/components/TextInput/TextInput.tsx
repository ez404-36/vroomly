import React from 'react';
import { clsx } from 'clsx';
import { inputBase, inputError, labelBase, errorBase } from './TextInput.styles';
import type { TextInputProps } from './TextInput.types';

export const TextInput = React.forwardRef<HTMLInputElement, TextInputProps>(
  ({ label, error, mt, wrapperClassName, className, required, ...rest }, ref) => {
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
          required={required}
          className={clsx(inputBase, error && inputError, className)}
          {...rest}
        />
        {error && <span className={errorBase}>{error}</span>}
      </div>
    );
  },
);

TextInput.displayName = 'TextInput';
