'use client'

import { useEffect, useRef } from 'react'
import { Bot, User, FileText } from 'lucide-react'
import { ScrollArea } from '@/components/ui/scroll-area'
import { LoadingSpinner } from './loading-spinner'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  fileName?: string
}

interface ChatMessagesProps {
  messages: Message[]
  isLoading: boolean
}

export function ChatMessages({ messages, isLoading }: ChatMessagesProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages])

  return (
    <ScrollArea className="flex-1 bg-background">
      <div className="space-y-4 p-6">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-muted-foreground py-12">
            <Bot size={48} className="mb-4 opacity-50" />
            <p className="text-lg">¿En qué puedo ayudarte?</p>
            <p className="text-sm mt-2">Carga un PDF o comienza a hacer preguntas</p>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-4 ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.role === 'assistant' && (
                  <div className="flex-shrink-0 mt-1">
                    <div className="w-8 h-8 rounded-full bg-primary/20 border border-primary/50 flex items-center justify-center">
                      <Bot size={18} className="text-primary" />
                    </div>
                  </div>
                )}

                <div
                  className={`max-w-md lg:max-w-2xl px-4 py-2 rounded-lg ${
                    message.role === 'user'
                      ? 'bg-emerald-600 text-white rounded-br-none'
                      : 'bg-muted text-foreground border border-border rounded-bl-none'
                  }`}
                >
                  {message.fileName && (
                    <div className="flex items-center gap-2 mb-2 px-2 py-1 bg-white/10 rounded text-xs font-medium border border-white/20">
                      <FileText size={14} className="text-white/80" />
                      <span className="truncate max-w-[200px]">{message.fileName}</span>
                    </div>
                  )}
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">
                    {message.content}
                  </p>
                </div>

                {message.role === 'user' && (
                  <div className="flex-shrink-0 mt-1">
                    <div className="w-8 h-8 rounded-full bg-accent flex items-center justify-center">
                      <User size={18} className="text-accent-foreground" />
                    </div>
                  </div>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="flex gap-4 animate-in fade-in slide-in-from-bottom-4 duration-300">
                <div className="flex-shrink-0 mt-1">
                  <div className="w-8 h-8 rounded-full bg-primary/20 border border-primary/50 flex items-center justify-center">
                    <Bot size={18} className="text-primary" />
                  </div>
                </div>
                <div className="bg-muted border border-border rounded-lg rounded-bl-none px-4 py-3 flex items-center gap-2">
                  <LoadingSpinner />
                  <span className="text-sm text-muted-foreground">La IA está escribiendo...</span>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={scrollRef} />
      </div>
    </ScrollArea>
  )
}
