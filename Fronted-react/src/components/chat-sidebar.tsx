'use client'

import { Plus, Trash2, Clock, Settings, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { cn } from '@/lib/utils'

import { ThemeSwitcher } from './theme-switcher'
import type {Chat} from "@/hooks/use-chat-local.ts";


interface ChatSidebarProps {
  chats: Chat[]
  currentChatId: string | null
  onNewChat: () => void
  onSelectChat: (chatId: string) => void
  onDeleteChat: (chatId: string) => void
  onClearAll: () => void
  onSettingsClick: () => void
  colorScheme: 'default' | 'white' | 'dark'
  onColorChange: (color: 'default' | 'white' | 'dark') => void
  onClose?: () => void
}

export function ChatSidebar({
  chats,
  currentChatId,
  onNewChat,
  onSelectChat,
  onDeleteChat,
  onClearAll,
  onSettingsClick,
  onClose,
}: ChatSidebarProps) {
  return (
    <div className="flex flex-col h-full bg-card text-foreground">
      {/* Header */}
      <div className="p-4 border-b border-border flex items-center justify-between gap-2">
        <Button
          onClick={onNewChat}
          className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white flex items-center justify-center gap-2"
        >
          <Plus size={20} />
          Nuevo Chat
        </Button>
        <Button variant="ghost" size="icon" onClick={onClose} className="text-muted-foreground">
          <X size={20} />
        </Button>
      </div>

      {/* Recent Chats */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="px-4 py-3 text-sm font-semibold text-muted-foreground flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Clock size={16} />
            Historial
          </div>
          {chats.length > 0 && (
            <button
              onClick={onClearAll}
              className="text-[10px] uppercase tracking-wider text-muted-foreground hover:text-destructive transition-colors"
              title="Borrar todo el historial"
            >
              Borrar todo
            </button>
          )}
        </div>

        <ScrollArea className="flex-1 px-2">
          <div className="space-y-2 pb-4">
            {chats.length === 0 ? (
              <div className="text-sm text-muted-foreground px-2 py-8 text-center">
                No hay chats aún.
              </div>
            ) : (
              chats.map((chat) => (
                <div
                  key={chat.id}
                  className={cn(
                    'group relative px-3 py-2 rounded-lg cursor-pointer text-sm transition-all',
                    currentChatId === chat.id
                      ? 'bg-emerald-600/20 text-emerald-600 dark:text-emerald-400 border border-emerald-500/50'
                      : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                  )}
                  onClick={() => onSelectChat(chat.id)}
                >
                  <div className="flex items-start justify-between gap-2 min-w-0">
                    <p className="truncate flex-1 font-medium">{chat.title}</p>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        onDeleteChat(chat.id)
                      }}
                      className="p-1 hover:bg-destructive/20 rounded transition-colors text-muted-foreground hover:text-destructive"
                      title="Eliminar chat"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </ScrollArea>
      </div>

      {/* Footer - SIEMPRE ABAJO */}
      <div className="p-4 border-t border-border bg-card/50 flex items-center justify-around mt-auto">
        <ThemeSwitcher />
        <Button
          variant="ghost"
          size="icon"
          onClick={onSettingsClick}
          className="text-muted-foreground hover:bg-accent hover:text-accent-foreground"
          title="Configuración"
        >
          <Settings size={20} />
        </Button>
      </div>
    </div>
  )
}
