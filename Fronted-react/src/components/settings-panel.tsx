'use client'

import { Settings, X, Zap, Lightbulb } from 'lucide-react'
import { useSettings, type Conciseness, type Speed } from '@/context/settings-context'

interface SettingsPanelProps {
  isOpen: boolean
  onClose: () => void
}

export function SettingsPanel({ isOpen, onClose }: SettingsPanelProps) {
  const { conciseness, setConciseness, speed, setSpeed } = useSettings()

  if (!isOpen) return null

  const conciseLevels: { value: Conciseness; label: string; description: string }[] = [
    { value: 'concise', label: 'Conciso', description: 'Respuestas cortas y directas' },
    { value: 'balanced', label: 'Equilibrado', description: 'Balance entre detalle y brevedad' },
    { value: 'detailed', label: 'Detallado', description: 'Respuestas completas y detalladas' },
  ]

  const speedLevels: { value: Speed; label: string; description: string }[] = [
    { value: 'fast', label: 'Rápido', description: 'Respuestas más rápidas' },
    { value: 'normal', label: 'Normal', description: 'Balance óptimo' },
  ]

  return (
    <>
      <div
        className="fixed inset-0 bg-black/50 z-40"
        onClick={onClose}
        aria-label="Cerrar settings"
      />

      <div className="fixed right-0 top-0 h-screen w-80 bg-card border-l border-border shadow-xl z-50 overflow-y-auto">
        <div className="sticky top-0 flex items-center justify-between p-4 border-b border-border bg-card">
          <div className="flex items-center gap-2">
            <Settings size={20} className="text-primary" />
            <h2 className="text-lg font-semibold text-foreground">Ajustes</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 hover:bg-accent rounded-lg transition-colors text-muted-foreground"
            aria-label="Cerrar"
          >
            <X size={20} />
          </button>
        </div>

        <div className="p-6 space-y-8">
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Lightbulb size={18} className="text-amber-500" />
              <h3 className="font-semibold text-foreground">Nivel de Detalle</h3>
            </div>

            <div className="space-y-2">
              {conciseLevels.map((level) => (
                <button
                  key={level.value}
                  onClick={() => setConciseness(level.value)}
                  className={`w-full text-left p-3 rounded-lg border-2 transition-all ${
                    conciseness === level.value
                      ? 'border-primary bg-primary/10'
                      : 'border-border bg-accent/30 hover:border-muted-foreground/30'
                  }`}
                >
                  <div className="font-medium text-foreground">{level.label}</div>
                  <div className="text-xs text-muted-foreground mt-1">{level.description}</div>
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Zap size={18} className="text-yellow-500" />
              <h3 className="font-semibold text-foreground">Velocidad</h3>
            </div>

            <div className="space-y-2">
              {speedLevels.map((level) => (
                <button
                  key={level.value}
                  onClick={() => setSpeed(level.value)}
                  className={`w-full text-left p-3 rounded-lg border-2 transition-all ${
                    speed === level.value
                      ? 'border-primary bg-primary/10'
                      : 'border-border bg-accent/30 hover:border-muted-foreground/30'
                  }`}
                >
                  <div className="font-medium text-foreground">{level.label}</div>
                  <div className="text-xs text-muted-foreground mt-1">{level.description}</div>
                </button>
              ))}
            </div>
          </div>
          <div className="pt-4 border-t border-border">
            <p className="text-xs text-muted-foreground text-center">
              Los ajustes se guardan automáticamente
            </p>
          </div>
        </div>
      </div>
    </>
  )
}
