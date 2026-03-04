'use client'

import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'

export type Theme = 'light' | 'dark' | 'default'
export type Conciseness = 'concise' | 'balanced' | 'detailed'
export type Speed = 'fast' | 'normal'

interface SettingsContextType {
  theme: Theme
  setTheme: (theme: Theme) => void
  conciseness: Conciseness
  setConciseness: (level: Conciseness) => void
  speed: Speed
  setSpeed: (speed: Speed) => void
}

const SettingsContext = createContext<SettingsContextType | undefined>(undefined)

export function SettingsProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<Theme>('default')
  const [conciseness, setConcatenessState] = useState<Conciseness>('balanced')
  const [speed, setSpeedState] = useState<Speed>('normal')
  const [mounted, setMounted] = useState(false)

  // Load from localStorage on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('chat-theme') as Theme | null
    const savedConciseness = localStorage.getItem('chat-conciseness') as Conciseness | null
    const savedSpeed = localStorage.getItem('chat-speed') as Speed | null

    if (savedTheme) setThemeState(savedTheme)
    if (savedConciseness) setConcatenessState(savedConciseness)
    if (savedSpeed) setSpeedState(savedSpeed)

    setMounted(true)
  }, [])

  // Apply theme to HTML element
  useEffect(() => {
    if (!mounted) return

    const html = document.documentElement
    html.classList.remove('light', 'dark')

    if (theme === 'default') {
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      if (isDark) html.classList.add('dark')
    } else {
      html.classList.add(theme)
    }
  }, [theme, mounted])

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme)
    localStorage.setItem('chat-theme', newTheme)
  }

  const setConciseness = (level: Conciseness) => {
    setConcatenessState(level)
    localStorage.setItem('chat-conciseness', level)
  }

  const setSpeed = (newSpeed: Speed) => {
    setSpeedState(newSpeed)
    localStorage.setItem('chat-speed', newSpeed)
  }

  return (
    <SettingsContext.Provider
      value={{
        theme,
        setTheme,
        conciseness,
        setConciseness,
        speed,
        setSpeed,
      }}
    >
      {children}
    </SettingsContext.Provider>
  )
}

export function useSettings() {
  const context = useContext(SettingsContext)
  if (!context) {
    throw new Error('useSettings debe estar dentro de SettingsProvider')
  }
  return context
}
