/* eslint-disable @typescript-eslint/no-explicit-any */
import { type MantineThemeOverride } from '@mantine/core';

export const theme: MantineThemeOverride = {
  primaryColor: 'yellow',

  fontFamily: 'Open Sans, sans-serif',

  colors: {
    brandOrange: [
      '#fff4e6', // 0
      '#ffe8cc', // 1
      '#ffd8a8', // 2
      '#ffb170', // 3 --blednyy-logo (lightOrange)
      '#ffa94d', // 4
      '#ff922b', // 5
      '#ff7300', // 6 ← primary --yarkiy (orangePrimary)
      '#f76707', // 7 ← hover
      '#e8590c', // 8
      '#d9480f', // 9
    ],

    brandNeutral: [
      '#ffffff', // 0 — white --chistyy-belyy (whiteMain)
      '#fffaf7', // 1 — warm white (whiteBackground)
      '#f2f2f2', // 2
      '#e0e0e0', // 3
      '#c7c7c7', // 4
      '#999999', // 5 — gray --bledno-seryy (lightGray)
      '#757575', // 6
      '#565656', // 7
      '#373737', // 8 — dark gray --tekst-osnovnoy (mainText)
      '#000000', // 9 — black
    ],

    differentColors: [
      '#ff7300', // 0 ← primary (orangePrimary)
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

  other: {
    colors: {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      background: (theme: any) =>
        theme.colorScheme === 'dark' ? theme.colors.dark[9] : theme.white,

      textPrimary: (theme: any) =>
        theme.colorScheme === 'dark' ? theme.white : theme.black,

      // Именованные константы для orange цветов
      lightOrange: (theme: any) => theme.colors.brandOrange[3],
      orangePrimary: (theme: any) => theme.colors.orange[6],
      orangeHover: (theme: any) => theme.colors.orange[7],
      orangeLight: (theme: any) => theme.colors.orange[0],
      orangeDark: (theme: any) => theme.colors.orange[9],
      // Именованные константы для neutral цветов
      whiteMain: (theme: any) => theme.colors.brandNeutral[0],
      whiteBackground: (theme: any) => theme.colors.brandNeutral[1],
      mainTextDarkGray: (theme: any) => theme.colors.brandNeutral[8],
      lightGray: (theme: any) => theme.colors.brandNeutral[5],
      // Именованные константы для different цветов
      dangerColor: (theme: any) => theme.colors.differentColors[5],
    },
  },
};