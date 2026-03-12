import { useState, useCallback, useEffect } from 'react'
import { Menu } from 'lucide-react'
import { ChatSidebar } from './components/chat-sidebar'
import { ChatMessages } from './components/chat-messages'
import { ChatInput } from './components/chat-input'
import { SettingsPanel } from './components/settings-panel'
import { useMobile } from './hooks/use-mobile'
import { useSettings } from './context/settings-context'
import { useChatLocal } from './hooks/use-chat-local'
import { Button } from './components/ui/button'
import { cn } from './lib/utils'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  fileName?: string
}

function App() {
  const { 
    chats, 
    currentChatId, 
    setCurrentChatId, 
    createNewChat, 
    updateChatMessages, 
    updateChatPDF, 
    deleteChat, 
    clearAllChats,
  } = useChatLocal()

  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isSettingsOpen, setIsSettingsOpen] = useState(false)
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const isMobile = useMobile()
  const { conciseness, speed } = useSettings()
  const [pdfLoaded, setPdfLoaded] = useState(false)
  const [pdfContent, setPdfContent] = useState('')
  const [pdfName, setPdfName] = useState('')

  useEffect(() => {
    const currentChat = chats.find(c => c.id === currentChatId)
    if (currentChat) {
      setMessages(currentChat.messages || [])
      setPdfContent('')
      setPdfName('')
      setPdfLoaded(false)
    } else if (chats.length > 0 && !currentChatId) {

    } else {
      setMessages([])
      setPdfContent('')
      setPdfName('')
      setPdfLoaded(false)
    }
    
    if (isMobile) {
      setIsSidebarOpen(false)
    }
  }, [currentChatId, chats.length, isMobile])

  const onSendMessage = useCallback(async (content: string, fileName?: string) => {
    let activeChatId = currentChatId
    

    if (!activeChatId) {
      const newChat = await createNewChat()
      if (!newChat) return
      activeChatId = newChat.id
    }

    const currentFile = fileName || pdfName

    const newMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      fileName: currentFile || undefined
    }
    
    const updatedMessages = [...messages, newMessage]
    setMessages(updatedMessages)
    updateChatMessages(activeChatId, updatedMessages)
    setIsLoading(true)

    const pdfContentToSend = pdfContent
    const pdfNameToSend = currentFile

    setPdfContent('')
    setPdfName('')
    setPdfLoaded(false)

    try {
      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: content,
          pdfContext: pdfContentToSend,
          chatId: activeChatId,
          fileName: pdfNameToSend,
          conciseness: conciseness,
          speed: speed
        }),
      })

      const data = await response.json()

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response || 'No response received from the server.',
      }

      const finalMessages = [...updatedMessages, assistantMessage]
      setMessages(finalMessages)
      updateChatMessages(activeChatId as string, finalMessages)

    } catch (error) {
      console.error('Error:', error)
    } finally {
      setIsLoading(false)
    }  }, [currentChatId, messages, pdfContent, pdfName, conciseness, speed, createNewChat, updateChatMessages])

  const onPdfUpload = useCallback(async (content: string, uploadChatId: string, fileName?: string) => {

  if (!content && !fileName) {
    updateChatPDF(uploadChatId, '', null)
    setPdfLoaded(false)
    setPdfContent('')
    setPdfName(null)
    return
  }


  const name = fileName || 'Documento PDF'
  updateChatPDF(uploadChatId, content, name)

  setPdfLoaded(true)
  setPdfContent(content)
  setPdfName(name)
}, [updateChatPDF])

  const [colorScheme, setColorScheme] = useState<'default' | 'white' | 'dark'>('default')

  const getOrCreatedChatId = useCallback(async () => {
    if (currentChatId) return currentChatId
    const newChat = await createNewChat()
    if (!newChat) return ""
    return newChat.id
  }, [currentChatId, createNewChat])

  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden relative">
      <div 
        className={cn(
          "fixed inset-0 z-50 bg-black/20 transition-opacity duration-300",
          isSidebarOpen ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"
        )}
        onClick={() => setIsSidebarOpen(false)}
      >
        <div 
          className={cn(
            "fixed inset-y-0 left-0 w-72 bg-card border-r border-border shadow-2xl transition-transform duration-300 ease-in-out",
            isSidebarOpen ? "translate-x-0" : "-translate-x-full"
          )}
          onClick={(e) => e.stopPropagation()}
        >
          <ChatSidebar
            chats={chats}
            currentChatId={currentChatId}
            onNewChat={createNewChat}
            onSelectChat={setCurrentChatId}
            onDeleteChat={deleteChat}
            onClearAll={clearAllChats}
            onSettingsClick={() => setIsSettingsOpen(true)}
            colorScheme={colorScheme}
            onColorChange={setColorScheme}
            onClose={() => setIsSidebarOpen(false)}
          />
        </div>
      </div>

      <main className="flex-1 flex flex-col relative w-full overflow-hidden">
        <header className="h-16 border-b border-border flex items-center px-6 bg-card/80 backdrop-blur-md justify-between z-10">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsSidebarOpen(true)}
              className="hover:bg-accent transition-colors"
              title="Ver Historial"
            >
              <Menu size={24} />
            </Button>
            <h1 className="text-xl font-bold bg-gradient-to-r from-emerald-400 to-emerald-500 bg-clip-text text-transparent">
              Asistente de IA RAG
            </h1>
          </div>
        </header>

        <ChatMessages messages={messages} isLoading={isLoading} />

        <ChatInput
          onSendMessage={onSendMessage}
          onPdfUpload={onPdfUpload}
          isLoading={isLoading}
          pdfLoaded={pdfLoaded}
          pdfName={pdfName}
          chatId={currentChatId}
          onGetOrCreatedChatId={getOrCreatedChatId}
        />

        <SettingsPanel
          isOpen={isSettingsOpen}
          onClose={() => setIsSettingsOpen(false)}
        />
      </main>
    </div>
  )
}

export default App
