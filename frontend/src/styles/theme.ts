/* eslint-disable @typescript-eslint/no-explicit-any */
import { type MantineThemeOverride } from '@mantine/core';

export const theme: MantineThemeOverride = {
  primaryColor: 'yellow',

  fontFamily: 'Open Sans, sans-serif',

  colors: {
    /** 🟧 ORANGE — brand, одинаковый для light/dark */
    orange: [
      '#fff4e6', // 0
      '#ffe8cc', // 1
      '#ffd8a8', // 2
      '#ffc078', // 3
      '#ffa94d', // 4
      '#ff922b', // 5
      '#fd7e14', // 6 ← primary
      '#f76707', // 7 ← hover
      '#e8590c', // 8
      '#d9480f', // 9
    ],
  },

  other: {
    colors: {
      background: (theme: any) =>
        theme.colorScheme === 'dark' ? theme.colors.dark[9] : theme.white,

      textPrimary: (theme: any) =>
        theme.colorScheme === 'dark' ? theme.white : theme.black,
    },
  },
};
