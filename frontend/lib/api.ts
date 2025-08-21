import { logout } from './auth'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface ChatResponse {
  content: string
  role: string
  confidence?: number
  sources?: string[]
  processing_time?: number
  response_type?: string
  user_info?: any
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: {
    username: string
    name: string
    email: string
    role: string
  }
}

export async function loginUser(credentials: LoginRequest): Promise<LoginResponse> {
  try {
    const formData = new URLSearchParams()
    formData.append('username', credentials.username.trim())
    formData.append('password', credentials.password.trim())

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      mode: 'cors',
      body: formData.toString(),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || 'Erro no login')
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('❌ Erro no login:', error)
    throw error
  }
}

function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem('access_token')
  
  if (token) {
    return {
      'Authorization': `Bearer ${token}`
    }
  }
  
  return {}
}

export async function sendMessage(message: string | { content: string }, conversationId?: string): Promise<ChatResponse> {
  const plain = typeof message === 'string' ? message : message?.content
  const trimmed = (plain ?? '').trim()
  if (!trimmed) throw new Error('Mensagem vazia')
  try {
    console.log('🚀 Enviando mensagem para:', `${API_BASE_URL}/chat`)
    const authHeaders = getAuthHeaders()

    const requestBody: any = { message: trimmed }
    if (conversationId) requestBody.conversation_id = conversationId
    console.log('🧾 Payload /chat:', requestBody)

    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders
      },
      body: JSON.stringify(requestBody)
    })

    console.log('📡 Response status:', response.status)

    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('user_data')
        window.location.href = '/login'
        throw new Error('Sessão expirada')
      }
      const errorData = await response.json().catch(() => ({}))
      console.error('❌ Erro /chat:', errorData)
      throw new Error(errorData.detail || 'Erro ao enviar mensagem')
    }

    const data = await response.json()
    console.log('🧾 Resposta /chat (raw):', data)
    const answer = data.response ?? data.content
    if (!answer) {
      throw new Error('Resposta não encontrada no payload')
    }
    return {
      content: answer,
      role: 'assistant',
      confidence: undefined,
      sources: [],
      processing_time: undefined,
      response_type: undefined,
      user_info: undefined
    }
  } catch (error) {
    console.error('❌ Exceção sendMessage:', error)
    throw error
  }
}