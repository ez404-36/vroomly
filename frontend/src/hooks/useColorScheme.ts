import { useState, useEffect, useCallback } from 'react';

export function useColorScheme(): {
  colorScheme: 'light' | 'dark';
  toggleColorScheme: () => void;
} {
  const [colorScheme, setColorScheme] = useState<'light' | 'dark'>(() => {
    return (localStorage.getItem('color-scheme') as 'light' | 'dark') ?? 'dark';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', colorScheme);
    localStorage.setItem('color-scheme', colorScheme);
  }, [colorScheme]);

  const toggleColorScheme = useCallback(() => {
    setColorScheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  }, []);

  return { colorScheme, toggleColorScheme };
}
