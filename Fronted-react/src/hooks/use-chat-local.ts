'use client'

import { useState, useEffect } from 'react'

export interface Chat {
  id: string
  title: string
  messages: any[]
  pdfContent: string | null
  pdfName: string | null
  createdAt: Date
  updatedAt: Date
}

const API_BASE_URL = 'http://127.0.0.1:8000'

export function useChatLocal() {
  const [chats, setChats] = useState<Chat[]>([])
  const [currentChatId, setCurrentChatId] = useState<string | null>(null)
  const [isLoaded, setIsLoaded] = useState(false)

  // Load chats from Database instead of localStorage
  useEffect(() => {
    const fetchChats = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/chats`)
        const data = await response.json()
        
        const parsedChats = data.chats.map((chat: any) => ({
          id: chat.id,
          title: chat.titulo,
          pdfName: chat.pdf_nombre,
          messages: (chat.messages || []).map((m: any) => ({
            id: m.id,
            role: m.role,
            content: m.content,
            fileName: m.fileName || null // Aquí aseguramos que React reciba fileName correctamente
          })),
          pdfContent: chat.pdf_content,
          createdAt: new Date(chat.fecha_creacion),
          updatedAt: new Date(chat.fecha_actualizacion),
        }))
        
        setChats(parsedChats)
        
        // Recuperar el último chat abierto de localStorage
        const lastChatId = localStorage.getItem('last_chat_id')
        
        if (lastChatId && parsedChats.some((c: Chat) => c.id === lastChatId)) {
          setCurrentChatId(lastChatId)
        } else if (parsedChats.length > 0) {
          setCurrentChatId(parsedChats[0].id)
        } else {
          // Si no hay chats en la DB, creamos el primero
          createNewChat()
        }
      } catch (e) {
        console.error('Error loading chats from DB:', e)
      } finally {
        setIsLoaded(true)
      }
    }
    fetchChats()
  }, [])

  // Persistir el chat actual en localStorage cuando cambie
  useEffect(() => {
    if (currentChatId) {
      localStorage.setItem('last_chat_id', currentChatId)
    }
  }, [currentChatId])

  const createNewChat = async () => {
    const newId = Date.now().toString()
    const newChat: Chat = {
      id: newId,
      title: 'Nueva conversación',
      messages: [],
      pdfContent: null,
      pdfName: null,
      createdAt: new Date(),
      updatedAt: new Date(),
    }
    
    try {
      const response = await fetch(`${API_BASE_URL}/chats`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: newId, title: newChat.title })
      })
      
      if (!response.ok) {
        throw new Error('Error al crear el chat en el servidor')
      }
      
      setChats(prevChats => [newChat, ...prevChats])
      setCurrentChatId(newId)
      return newChat
    } catch (error) {
      console.error('Error creating chat in DB:', error)
      alert('Error al crear una nueva conversación en la base de datos.')
      return null
    }
  }

  const updateChatMessages = (chatId: string, messages: any[]) => {
    // Los mensajes se guardan en la DB automáticamente vía el endpoint /chat
    // Aquí solo actualizamos el estado local para la UI inmediata
    setChats(prevChats => {
      return prevChats.map((chat) =>
        chat.id === chatId
          ? {
              ...chat,
              messages,
              title:
                messages.length > 0 && messages[0].role === 'user'
                  ? messages[0].content.substring(0, 25).trim() + (messages[0].content.length > 25 ? "..." : "")
                  : chat.title,
              updatedAt: new Date(),
            }
          : chat
      )
    })
  }

  const updateChatPDF = (chatId: string, pdfContent: string, pdfName: string) => {
    // Actualizamos el estado local para que la UI refleje el cambio inmediatamente
    setChats(prevChats => {
      return prevChats.map((chat) =>
        chat.id === chatId
          ? {
              ...chat,
              pdfContent: pdfContent,
              pdfName: pdfName,
              updatedAt: new Date(),
            }
          : chat
      )
    })
  }

  const deleteChat = async (chatId: string) => {
    try {
      await fetch(`${API_BASE_URL}/chats/${chatId}`, { method: 'DELETE' })
      const updatedChats = chats.filter((chat) => chat.id !== chatId)
      setChats(updatedChats)
      if (currentChatId === chatId) {
        setCurrentChatId(updatedChats[0]?.id || null)
      }
    } catch (error) {
      console.error('Error deleting chat:', error)
    }
  }

  const clearAllChats = async () => {
    if (window.confirm('¿Estás seguro de que quieres borrar todo el historial?')) {
      try {
        await fetch(`${API_BASE_URL}/chats`, { method: 'DELETE' })
        setChats([])
        setCurrentChatId(null)
      } catch (error) {
        console.error('Error clearing chats:', error)
      }
    }
  }

  const getCurrentChat = () => {
    return chats.find((chat) => chat.id === currentChatId)
  }

  return {
    chats,
    currentChatId,
    isLoaded,
    createNewChat,
    setCurrentChatId,
    updateChatMessages,
    updateChatPDF,
    deleteChat,
    clearAllChats,
    getCurrentChat,
  }
}
