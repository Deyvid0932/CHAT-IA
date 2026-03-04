'use client'

import { useState, useEffect } from 'react'

export interface Chat {
  id: string

  title: string
  messages: any[]
  pdfContent: string | null
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
          ...chat,
          createdAt: new Date(chat.fecha_creacion),
          updatedAt: new Date(chat.fecha_actualizacion),
        }))
        
        if (parsedChats.length > 0) {
          setChats(parsedChats)
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

  const createNewChat = async () => {
    const newId = Date.now().toString()
    const newChat: Chat = {
      id: newId,
      title: 'Nueva conversación',
      messages: [],
      pdfContent: null,
      createdAt: new Date(),
      updatedAt: new Date(),
    }
    
    try {
      await fetch(`${API_BASE_URL}/chats`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: newId, title: newChat.title })
      })
      
      setChats(prevChats => [newChat, ...prevChats])
      setCurrentChatId(newId)
    } catch (error) {
      console.error('Error creating chat in DB:', error)
    }
    
    return newChat
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

  const updateChatPDF = (chatId: string, pdfContent: string) => {
    // Podríamos añadir un endpoint para esto, pero por ahora lo mantenemos en memoria
    // o lo guardamos si el usuario lo sube.
    setChats(prevChats => {
      return prevChats.map((chat) =>
        chat.id === chatId
          ? {
              ...chat,
              pdfContent,
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
