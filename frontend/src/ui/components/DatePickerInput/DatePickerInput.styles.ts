import React from 'react';

export const triggerBase =
  'flex h-9 w-full items-center justify-between rounded-(--radius) border border-(--color-border) bg-(--color-input-bg) px-3 py-2 text-sm text-(--color-text) focus:outline-none focus:ring-2 focus:ring-(--ring) disabled:opacity-50 disabled:cursor-not-allowed transition-colors';

export const popoverContent =
  'z-50 rounded-(--radius) border border-(--color-border) bg-(--color-surface) p-4 shadow-lg text-(--color-text)';

export const dayPickerStyles = {
  '--rdp-cell-size': '36px',
  '--rdp-accent-color': 'var(--color-primary)',
  '--rdp-background-color': 'var(--color-primary-subtle)',
} as React.CSSProperties;
