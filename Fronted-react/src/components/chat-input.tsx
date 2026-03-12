'use client'
import { useState, useRef } from 'react'
import { Send, Upload, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { LoadingSpinner } from './loading-spinner'

interface ChatInputProps {
  onSendMessage: (message: string, fileName?: string) => void
  onPdfUpload: (content: string, chatId: string, fileName?: string) => void
  isLoading: boolean
  pdfLoaded: boolean
  pdfName?: string | null
  chatId: string | null
  onGetOrCreatedChatId: () => Promise<string>
  onSettingsClick?: () => void
}

export function ChatInput({
  onSendMessage,
  onPdfUpload,
  isLoading,
  pdfLoaded,
  pdfName,
  chatId,
  onGetOrCreatedChatId
}: ChatInputProps) {
  const [input, setInput] = useState('')
  const [pdfFile, setPdfFile] = useState<File | null>(null)
  const [extracting, setExtracting] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim() && !isLoading) {
      onSendMessage(input, pdfFile?.name || (pdfLoaded ? pdfName || undefined : undefined))
      setInput('')
      setPdfFile(null)
    }
  }

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (file.type !== 'application/pdf') {
      alert('Por favor, selecciona un archivo PDF válido.')
      return
    }

    setPdfFile(file)
    setExtracting(true)

    try {

      const activeChatId = chatId || await onGetOrCreatedChatId()

      const formData = new FormData()
      formData.append('file', file)
      formData.append('chat_id', activeChatId)

      const response = await fetch('http://127.0.0.1:8000/upload', {
        method: 'POST',
        body: formData,
      })
      const data = await response.json()
      onPdfUpload(data.text, activeChatId, file.name)
    } catch (error) {
      console.error('Error al subir PDF:', error)
      alert('Error al conectar con el backend para procesar el PDF.')
    } finally {
      setExtracting(false)
    }
  }

  const handleBorrarTodo = async () => {
  const nameToDelete = currentFileName;

  if (nameToDelete && chatId) {
    try {
      const encodedName = encodeURIComponent(nameToDelete);

      const url = `http://127.0.0.1:8000/delete-pdf/${chatId}/${encodedName}`;

      const response = await fetch(url, { method: 'DELETE' });

      if (response.ok) {
        console.log("✅ Backend: Chunks deleted");
      } else {
        console.error("❌ Backend responded with error:", response.status);
      }
    } catch (error) {
      console.error("❌ Network error when trying to delete:", error);
    }
  }

  onPdfUpload('', chatId || '', '');

  setPdfFile(null);
  if (fileInputRef.current) {
    fileInputRef.current.value = '';
  }
};

  const currentFileName = pdfFile?.name || (pdfLoaded ? pdfName : null)

  return (
    <div className="bg-card border-t border-border p-4 space-y-3">
      {/* PDF Status */}
      {currentFileName && (
        <div className="bg-emerald-600/10 border border-emerald-600/50 rounded-lg p-3 flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm text-emerald-600 dark:text-emerald-400">
            <Upload size={16} />
            <span className="truncate">{currentFileName}</span>
          </div>
          <button
            onClick={handleBorrarTodo}
            className="text-emerald-600 hover:text-emerald-500 transition-colors"
          >
            <X size={18} />
          </button>
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="flex gap-2 px-4 py-3">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Escribe tu pregunta..."
          disabled={isLoading || extracting}
          className="flex-1 bg-background border-input text-foreground placeholder:text-muted-foreground"
        />

        <input
          ref={fileInputRef}
          type="file"
          accept="application/pdf"
          onChange={handleFileSelect}
          disabled={extracting}
          className="hidden"
        />

        <Button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={extracting || isLoading}
          variant="outline"
          size="icon"
          className="border-input text-muted-foreground hover:bg-accent"
          title="Cargar PDF"
        >
          <Upload size={20} />
        </Button>

        <Button
          type="submit"
          disabled={isLoading || extracting || !input.trim()}
          className="bg-emerald-600 hover:bg-emerald-700 text-white flex items-center gap-2"
          size="default"
        >
          {isLoading ? (
            <>
              <LoadingSpinner />
              <span className="hidden sm:inline">Enviando</span>
            </>
          ) : (
            <>
              <Send size={20} />
              <span className="hidden sm:inline">Enviar</span>
            </>
          )}
        </Button>

      </form>

      <p className="text-xs text-muted-foreground text-center px-4 pb-2">
        {extracting ? 'Procesando PDF...' : 'Haz preguntas sobre tu PDF o chatea con la IA'}
      </p>
    </div>
  )
}
