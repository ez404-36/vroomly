import React, { useState } from 'react';
import * as Popover from '@radix-ui/react-popover';
import { DayPicker } from 'react-day-picker';
import { clsx } from 'clsx';
import { triggerBase, popoverContent } from './DatePickerInput.styles';
import { labelBase, errorBase } from '../TextInput/TextInput.styles';
import type { DatePickerInputProps } from './DatePickerInput.types';

function formatDate(date: Date): string {
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();
  return `${day}-${month}-${year}`;
}

export const DatePickerInput = React.forwardRef<HTMLButtonElement, DatePickerInputProps>(
  ({ label, placeholder = 'Выберите дату', value, onChange, error, disabled = false, required = false, clearable = false, maxDate, className }, ref) => {
    const [open, setOpen] = useState(false);

    const handleSelect = (day: Date | undefined) => {
      onChange?.(day ?? null);
      if (day) setOpen(false);
    };

    const handleClear = (e: React.MouseEvent) => {
      e.stopPropagation();
      onChange?.(null);
    };

    return (
      <div className={clsx('flex flex-col', className)}>
        {label && (
          <label className={labelBase}>
            {label}
            {required && <span className="text-[--color-danger] ml-0.5">*</span>}
          </label>
        )}
        <Popover.Root open={open} onOpenChange={setOpen}>
          <Popover.Trigger asChild>
            <button
              ref={ref}
              type="button"
              disabled={disabled}
              className={clsx(triggerBase, error && 'border-[--color-danger] focus:ring-[--color-danger]')}
            >
              <span className={value ? 'text-[--color-text]' : 'text-[--color-text-muted]'}>
                {value ? formatDate(value) : placeholder}
              </span>
              <span className="flex items-center gap-1 ml-auto">
                {clearable && value && (
                  <span
                    role="button"
                    tabIndex={0}
                    onClick={handleClear}
                    onKeyDown={(e) => e.key === 'Enter' && handleClear(e as unknown as React.MouseEvent)}
                    className="text-[--color-text-muted] hover:text-[--color-text] cursor-pointer"
                    aria-label="Очистить дату"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <line x1="18" y1="6" x2="6" y2="18" />
                      <line x1="6" y1="6" x2="18" y2="18" />
                    </svg>
                  </span>
                )}
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect width="18" height="18" x="3" y="4" rx="2" ry="2" />
                  <line x1="16" x2="16" y1="2" y2="6" />
                  <line x1="8" x2="8" y1="2" y2="6" />
                  <line x1="3" x2="21" y1="10" y2="10" />
                </svg>
              </span>
            </button>
          </Popover.Trigger>
          <Popover.Portal>
            <Popover.Content className={popoverContent} side="top" sideOffset={4} align="start">
              <DayPicker
                mode="single"
                selected={value ?? undefined}
                onSelect={handleSelect}
                disabled={maxDate ? { after: maxDate } : undefined}
                style={{
                  '--rdp-accent-color': 'var(--color-primary)',
                  '--rdp-background-color': 'var(--color-primary-subtle)',
                } as React.CSSProperties}
              />
            </Popover.Content>
          </Popover.Portal>
        </Popover.Root>
        {error && <span className={errorBase}>{error}</span>}
      </div>
    );
  },
);

DatePickerInput.displayName = 'DatePickerInput';
