import React, { useState, useMemo, useRef, useEffect, useCallback } from 'react';
import * as Popover from '@radix-ui/react-popover';
import { useVirtualizer } from '@tanstack/react-virtual';
import { clsx } from 'clsx';
import { triggerBase, contentBase, itemBase, itemIndicatorBase } from './Select.styles';
import { labelBase, errorBase, inputBase } from '../TextInput/TextInput.styles';
import type { SelectProps, SelectOption } from './Select.types';

const ITEM_HEIGHT = 32;
const MAX_VISIBLE_ITEMS = 8;
const CLEAR_VALUE = '__clear__';

type InternalOption = SelectOption & { __clear?: boolean };

export const Select = React.forwardRef<HTMLButtonElement, SelectProps>(
  (
    {
      label,
      placeholder = 'Выберите...',
      value,
      onChange,
      options,
      data,
      error,
      disabled = false,
      searchable = false,
      clearable = false,
      required = false,
      className,
    },
    ref,
  ) => {
    const [open, setOpen] = useState(false);
    const [search, setSearch] = useState('');
    const [highlightedIndex, setHighlightedIndex] = useState(0);

    const allOptions = options ?? data ?? [];
    const [listEl, setListEl] = useState<HTMLDivElement | null>(null);
    const searchInputRef = useRef<HTMLInputElement>(null);

    const filteredOptions = useMemo(() => {
      if (!searchable || !search) return allOptions;
      const q = search.toLowerCase();
      return allOptions.filter((o) => o.label.toLowerCase().includes(q));
    }, [allOptions, searchable, search]);

    const displayOptions = useMemo<InternalOption[]>(() => {
      if (clearable && value) {
        return [{ value: CLEAR_VALUE, label: 'Очистить', __clear: true }, ...filteredOptions];
      }
      return filteredOptions;
    }, [filteredOptions, clearable, value]);

    const selectedOption = useMemo(
      () => allOptions.find((o) => o.value === value),
      [allOptions, value],
    );

    const rowVirtualizer = useVirtualizer({
      count: displayOptions.length,
      getScrollElement: () => listEl,
      estimateSize: () => ITEM_HEIGHT,
      overscan: 8,
    });

    useEffect(() => {
      if (!open) {
        setSearch('');
        return;
      }
      const idx = displayOptions.findIndex((o) => o.value === value);
      const next = idx >= 0 ? idx : 0;
      setHighlightedIndex(next);
      requestAnimationFrame(() => {
        if (listEl) {
          rowVirtualizer.scrollToIndex(next, { align: 'auto' });
        }
      });
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [open, listEl]);

    useEffect(() => {
      setHighlightedIndex(0);
    }, [search]);

    const handleSelect = useCallback(
      (opt: InternalOption) => {
        if (opt.__clear) {
          onChange?.(null);
        } else {
          onChange?.(opt.value);
        }
        setOpen(false);
      },
      [onChange],
    );

    const handleKeyDown = (e: React.KeyboardEvent) => {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setHighlightedIndex((i) => {
          const next = Math.min(i + 1, displayOptions.length - 1);
          rowVirtualizer.scrollToIndex(next, { align: 'auto' });
          return next;
        });
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setHighlightedIndex((i) => {
          const prev = Math.max(i - 1, 0);
          rowVirtualizer.scrollToIndex(prev, { align: 'auto' });
          return prev;
        });
      } else if (e.key === 'Home') {
        e.preventDefault();
        setHighlightedIndex(0);
        rowVirtualizer.scrollToIndex(0, { align: 'auto' });
      } else if (e.key === 'End') {
        e.preventDefault();
        const last = displayOptions.length - 1;
        setHighlightedIndex(last);
        rowVirtualizer.scrollToIndex(last, { align: 'auto' });
      } else if (e.key === 'Enter') {
        e.preventDefault();
        const opt = displayOptions[highlightedIndex];
        if (opt) handleSelect(opt);
      } else if (e.key === 'Escape') {
        e.preventDefault();
        setOpen(false);
      }
    };

    return (
      <div className={clsx('flex flex-col', className)}>
        {label && (
          <label className={labelBase}>
            {label}
            {required && <span className="text-(--color-danger) ml-0.5">*</span>}
          </label>
        )}
        <Popover.Root open={open} onOpenChange={setOpen}>
          <Popover.Trigger asChild>
            <button
              ref={ref}
              type="button"
              disabled={disabled}
              className={clsx(
                triggerBase,
                error && 'border-(--color-danger) focus:ring-(--color-danger)',
              )}
            >
              <span
                className={clsx('truncate', !selectedOption && 'text-(--color-text-muted)')}
              >
                {selectedOption?.label ?? placeholder}
              </span>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="ml-2 shrink-0"
              >
                <path d="m6 9 6 6 6-6" />
              </svg>
            </button>
          </Popover.Trigger>

          <Popover.Portal>
            <Popover.Content
              className={contentBase}
              align="start"
              sideOffset={4}
              style={{ zIndex: 9999, width: 'var(--radix-popover-trigger-width)' }}
              onOpenAutoFocus={(e) => {
                if (searchable) {
                  e.preventDefault();
                  searchInputRef.current?.focus();
                }
              }}
              onKeyDown={handleKeyDown}
            >
              {searchable && (
                <div className="p-1">
                  <input
                    ref={searchInputRef}
                    type="text"
                    className={clsx(inputBase, 'h-8 text-xs')}
                    placeholder="Поиск..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                  />
                </div>
              )}
              <div
                ref={setListEl}
                className="overflow-auto p-1"
                style={{ maxHeight: ITEM_HEIGHT * MAX_VISIBLE_ITEMS }}
              >
                {displayOptions.length === 0 ? (
                  <div className="py-2 px-3 text-sm text-(--color-text-muted)">
                    Нет результатов
                  </div>
                ) : (
                  <div
                    style={{
                      height: rowVirtualizer.getTotalSize(),
                      position: 'relative',
                      width: '100%',
                    }}
                  >
                    {rowVirtualizer.getVirtualItems().map((virtualRow) => {
                      const opt = displayOptions[virtualRow.index];
                      const isSelected = !opt.__clear && opt.value === value;
                      const isHighlighted = virtualRow.index === highlightedIndex;
                      return (
                        <div
                          key={virtualRow.key}
                          role="option"
                          aria-selected={isSelected}
                          className={clsx(
                            itemBase,
                            isHighlighted && 'bg-(--color-ghost-hover)',
                            opt.__clear && 'text-(--color-text-muted) italic',
                          )}
                          style={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            width: '100%',
                            height: virtualRow.size,
                            transform: `translateY(${virtualRow.start}px)`,
                          }}
                          onClick={() => handleSelect(opt)}
                          onMouseEnter={() => setHighlightedIndex(virtualRow.index)}
                        >
                          {isSelected && (
                            <span className={itemIndicatorBase}>
                              <svg
                                xmlns="http://www.w3.org/2000/svg"
                                width="12"
                                height="12"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="3"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                              >
                                <polyline points="20 6 9 17 4 12" />
                              </svg>
                            </span>
                          )}
                          <span className="truncate">{opt.label}</span>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </Popover.Content>
          </Popover.Portal>
        </Popover.Root>
        {error && <span className={errorBase}>{error}</span>}
      </div>
    );
  },
);

Select.displayName = 'Select';
