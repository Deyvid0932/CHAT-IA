'use client'

import { Sun, Moon, Monitor } from 'lucide-react'
import { useSettings, type Theme } from '@/context/settings-context'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Button } from '@/components/ui/button'

export function ThemeSwitcher() {
  const { theme, setTheme } = useSettings()

  const themeOptions: { value: Theme; label: string; icon: React.ReactNode }[] = [
    { value: 'light', label: 'Claro', icon: <Sun size={16} /> },
    { value: 'dark', label: 'Oscuro', icon: <Moon size={16} /> },
    { value: 'default', label: 'Sistema', icon: <Monitor size={16} /> },
  ]

  const currentTheme = themeOptions.find((t) => t.value === theme)

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="text-muted-foreground hover:bg-accent hover:text-primary transition-colors"
          title={`Tema actual: ${currentTheme?.label}`}
        >
          {currentTheme?.icon}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="bg-card border-border">
        {themeOptions.map((option) => (
          <DropdownMenuItem
            key={option.value}
            onClick={() => setTheme(option.value)}
            className={`cursor-pointer flex items-center gap-2 ${
              theme === option.value
                ? 'bg-primary/10 text-primary'
                : 'text-muted-foreground hover:bg-accent'
            }`}
          >
            {option.icon}
            <span>{option.label}</span>
            {theme === option.value && (
              <span className="ml-auto text-primary">✓</span>
            )}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
