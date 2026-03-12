'use client'

import { useMemo } from 'react'
import { useSettings } from '@/context/settings-context'

export interface ThemeColors {

  bg: {
    main: string
    sidebar: string
    card: string
    input: string
    hover: string
  }

  text: {
    primary: string
    secondary: string
    muted: string
  }

  accent: {
    primary: string
    secondary: string
    hover: string
    light: string
  }

  border: string
}

export function useThemeColors(): ThemeColors {
  const { theme } = useSettings()

  return useMemo(() => {
    const isDark =
      theme === 'dark' ||
      (theme === 'default' &&
        typeof window !== 'undefined' &&
        window.matchMedia('(prefers-color-scheme: dark)').matches)

    if (isDark) {

      return {
        bg: {
          main: 'bg-slate-950',
          sidebar: 'bg-slate-900',
          card: 'bg-slate-800',
          input: 'bg-slate-800',
          hover: 'hover:bg-slate-700',
        },
        text: {
          primary: 'text-white',
          secondary: 'text-slate-300',
          muted: 'text-slate-400',
        },
        accent: {
          primary: 'bg-emerald-700',
          secondary: 'bg-blue-900',
          hover: 'hover:bg-emerald-600',
          light: 'text-emerald-400',
        },
        border: 'border-slate-700',
      }
    } else {

      return {
        bg: {
          main: 'bg-slate-50',
          sidebar: 'bg-white',
          card: 'bg-white',
          input: 'bg-gray-100',
          hover: 'hover:bg-slate-100',
        },
        text: {
          primary: 'text-slate-900',
          secondary: 'text-slate-600',
          muted: 'text-slate-500',
        },
        accent: {
          primary: 'bg-green-500',
          secondary: 'bg-blue-400',
          hover: 'hover:bg-green-600',
          light: 'text-green-600',
        },
        border: 'border-slate-200',
      }
    }
  }, [theme])
}
