'use client'

import { useMemo } from 'react'
import { useSettings } from '@/context/settings-context'

export interface ThemeColors {
  // Background colors
  bg: {
    main: string
    sidebar: string
    card: string
    input: string
    hover: string
  }
  // Text colors
  text: {
    primary: string
    secondary: string
    muted: string
  }
  // Accent colors
  accent: {
    primary: string
    secondary: string
    hover: string
    light: string
  }
  // Border colors
  border: string
}

export function useThemeColors(): ThemeColors {
  const { theme } = useSettings()

  return useMemo(() => {
    // Determine if dark theme is active
    const isDark =
      theme === 'dark' ||
      (theme === 'default' &&
        typeof window !== 'undefined' &&
        window.matchMedia('(prefers-color-scheme: dark)').matches)

    if (isDark) {
      // Dark theme with dark blue and dark green
      return {
        bg: {
          main: 'bg-slate-950', // Very dark background
          sidebar: 'bg-slate-900', // Slightly lighter sidebar
          card: 'bg-slate-800', // Card background
          input: 'bg-slate-800', // Input field
          hover: 'hover:bg-slate-700', // Hover state
        },
        text: {
          primary: 'text-white',
          secondary: 'text-slate-300',
          muted: 'text-slate-400',
        },
        accent: {
          primary: 'bg-emerald-700', // Dark green
          secondary: 'bg-blue-900', // Dark blue
          hover: 'hover:bg-emerald-600',
          light: 'text-emerald-400',
        },
        border: 'border-slate-700',
      }
    } else {
      // Light theme with light green and light backgrounds
      return {
        bg: {
          main: 'bg-slate-50', // Very light background
          sidebar: 'bg-white', // White sidebar
          card: 'bg-white', // White card
          input: 'bg-gray-100', // Light gray input
          hover: 'hover:bg-slate-100', // Light hover
        },
        text: {
          primary: 'text-slate-900',
          secondary: 'text-slate-600',
          muted: 'text-slate-500',
        },
        accent: {
          primary: 'bg-green-500', // Light green
          secondary: 'bg-blue-400', // Light blue
          hover: 'hover:bg-green-600',
          light: 'text-green-600',
        },
        border: 'border-slate-200',
      }
    }
  }, [theme])
}
