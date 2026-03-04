'use client'

import { Palette } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuLabel,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu'

type ColorScheme = 'default' | 'white' | 'dark'

interface ColorThemeButtonProps {
  onColorChange?: (color: ColorScheme) => void
  currentColor?: ColorScheme
}

export function ColorThemeButton({
  onColorChange,
  currentColor = 'default',
}: ColorThemeButtonProps) {
  const colorOptions: { value: ColorScheme; label: string; description: string }[] = [
    {
      value: 'default',
      label: 'Default',
      description: 'Tema predeterminado oscuro',
    },
    {
      value: 'white',
      label: 'Blanco',
      description: 'Tema claro minimalista',
    },
    {
      value: 'dark',
      label: 'Negro',
      description: 'Tema ultra oscuro',
    },
  ]

  const getColorPreview = (color: ColorScheme) => {
    switch (color) {
      case 'white':
        return 'bg-white'
      case 'dark':
        return 'bg-black'
      default:
        return 'bg-slate-800'
    }
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="text-muted-foreground hover:bg-accent hover:text-primary transition-colors"
          title="Cambiar color del tema"
        >
          <Palette size={20} />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="bg-card border-border w-56">
        <DropdownMenuLabel className="text-foreground">Esquema de Colores</DropdownMenuLabel>
        <DropdownMenuSeparator className="bg-border" />
        {colorOptions.map((option) => (
          <DropdownMenuItem
            key={option.value}
            onClick={() => onColorChange?.(option.value)}
            className={`cursor-pointer flex items-start justify-between py-3 px-3 ${
              currentColor === option.value
                ? 'bg-primary/10 text-primary'
                : 'text-muted-foreground hover:bg-accent'
            }`}
          >
            <div className="flex items-start gap-3 flex-1">
              <div
                className={`w-4 h-4 rounded-full mt-1 flex-shrink-0 border border-border ${getColorPreview(
                  option.value
                )}`}
              />
              <div>
                <div className="font-medium text-sm">{option.label}</div>
                <div className="text-xs opacity-70 mt-0.5">
                  {option.description}
                </div>
              </div>
            </div>
            {currentColor === option.value && (
              <span className="text-primary ml-2">✓</span>
            )}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
