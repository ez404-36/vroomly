import React, { useState, useMemo } from 'react';
import * as RadixSelect from '@radix-ui/react-select';
import { clsx } from 'clsx';
import { triggerBase, contentBase, itemBase, itemIndicatorBase } from './Select.styles';
import { labelBase, errorBase } from '../TextInput/TextInput.styles';
import { inputBase } from '../TextInput/TextInput.styles';
import type { SelectProps } from './Select.types';

export const Select = React.forwardRef<HTMLButtonElement, SelectProps>(
  ({ label, placeholder = 'Выберите...', value, onChange, options, data, error, disabled = false, searchable = false, clearable = false, required = false, className }, ref) => {
    const [search, setSearch] = useState('');
    const allOptions = options ?? data ?? [];

    const filteredOptions = useMemo(() => {
      if (!searchable || !search) return allOptions;
      return allOptions.filter((o) => o.label.toLowerCase().includes(search.toLowerCase()));
    }, [allOptions, searchable, search]);

    const handleValueChange = (v: string) => {
      if (v === '__clear__') {
        onChange?.(null);
      } else {
        onChange?.(v || null);
      }
    };

    return (
      <div className={clsx('flex flex-col', className)}>
        {label && (
          <label className={labelBase}>
            {label}
            {required && <span className="text-[--color-danger] ml-0.5">*</span>}
          </label>
        )}
        <RadixSelect.Root
          value={value ?? undefined}
          onValueChange={handleValueChange}
          disabled={disabled}
        >
          <RadixSelect.Trigger
            ref={ref}
            className={clsx(triggerBase, error && 'border-[--color-danger] focus:ring-[--color-danger]')}
          >
            <RadixSelect.Value placeholder={placeholder} />
            <RadixSelect.Icon className="ml-auto">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="m6 9 6 6 6-6" />
              </svg>
            </RadixSelect.Icon>
          </RadixSelect.Trigger>

          <RadixSelect.Portal>
            <RadixSelect.Content className={contentBase} position="popper" sideOffset={4}>
              {searchable && (
                <div className="p-1">
                  <input
                    type="text"
                    className={clsx(inputBase, 'h-8 text-xs')}
                    placeholder="Поиск..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    onKeyDown={(e) => e.stopPropagation()}
                  />
                </div>
              )}
              <RadixSelect.Viewport className="p-1">
                {clearable && value && (
                  <RadixSelect.Item value="__clear__" className={itemBase}>
                    <RadixSelect.ItemText className="text-[--color-text-muted] italic">Очистить</RadixSelect.ItemText>
                  </RadixSelect.Item>
                )}
                {filteredOptions.map((option) => (
                  <RadixSelect.Item key={option.value} value={option.value} className={itemBase}>
                    <span className={itemIndicatorBase}>
                      <RadixSelect.ItemIndicator>
                        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                          <polyline points="20 6 9 17 4 12" />
                        </svg>
                      </RadixSelect.ItemIndicator>
                    </span>
                    <RadixSelect.ItemText>{option.label}</RadixSelect.ItemText>
                  </RadixSelect.Item>
                ))}
                {filteredOptions.length === 0 && (
                  <div className="py-2 px-3 text-sm text-[--color-text-muted]">Нет результатов</div>
                )}
              </RadixSelect.Viewport>
            </RadixSelect.Content>
          </RadixSelect.Portal>
        </RadixSelect.Root>
        {error && <span className={errorBase}>{error}</span>}
      </div>
    );
  },
);

Select.displayName = 'Select';
