/* eslint-disable @typescript-eslint/no-explicit-any */
import { type MantineThemeOverride } from '@mantine/core';

export const theme: MantineThemeOverride = {
  primaryColor: 'orange',

  fontFamily: 'Open Sans, sans-serif',

  colors: {
    brandOrange: [
      '#fff4ed', // 0
      '#ffe7d2', // 1
      '#ffd8a8', // 2
      '#ffb170', // 3
      '#ffa94d', // 4
      '#ff9742', // 5
      '#ff7300', // 6 ← primary
      '#f76707', // 7 ← hover
      '#e8590c', // 8
      '#d9480f', // 9
    ],

    brandNeutral: [
      '#ffffff', // 0 — white
      '#fffaf7', // 1 — warm white
      '#f2f2f2', // 2
      '#e0e0e0', // 3
      '#c7c7c7', // 4
      '#999999', // 5 — gray
      '#757575', // 6
      '#565656', // 7
      '#373737', // 8 — dark gray -
      '#000000', // 9 — black
    ],

    differentColors: [
      '#ff7300', // 0 ← primary
      '#008cff', // 1 — blue
      '#0dff00', // 2 — green
      '#f300ff', // 3 — magenta
      '#ffc107', // 4 — amber
      '#d20000', // 5 — red
      '#00bcd4', // 6 — cyan
      '#7b1fa2', // 7 — purple
      '#43a047', // 8 — green (тёмный)
      '#ff5722', // 9 — deep orange
    ],
  },

  headings: {
    fontFamily: 'Roboto, sans-serif',
    sizes: {
      h1: { fontSize: '56px' },
      h2: { fontSize: '40px' },
      h3: { fontSize: '32px' },
    },
  },
  // cssVariablesResolver передаётся в MantineProvider (main.tsx), не в theme

  other: {
    colors: {
      background: (theme: any) =>
        theme.colorScheme === 'dark' ? theme.colors.dark[9] : theme.white,

      textPrimary: (theme: any) =>
        theme.colorScheme === 'dark' ? theme.white : theme.dark[9],

      // Именованные константы для orange цветов
      lightOrange: (theme: any) => theme.colors.brandOrange[3],
      primaryColor: (theme: any) => theme.colors.orange[6],
      primaryColorHover: (theme: any) => theme.colors.orange[7],
      orangeDarkColor: (theme: any) => theme.colors.orange[9],
      // Именованные константы для neutral цветов
      white: (theme: any) => theme.colors.brandNeutral[0],
      backgroundPrimaryColor: (theme: any) => theme.colors.brandNeutral[1],
      textPrimaryColor: (theme: any) => theme.colors.brandNeutral[8],
      textSecondaryColor: (theme: any) => theme.colors.brandNeutral[5],
      // Именованные константы для different цветов
      dangerPrimaryColor: (theme: any) => theme.colors.differentColors[5],
    },
  },
};
