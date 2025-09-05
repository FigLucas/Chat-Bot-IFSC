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

export async function sendMessage(message: string | { content: string }, conversationId?: string, history?: { role: string, content: string }[]) {
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  const token = typeof window !== 'undefined' ? (localStorage.getItem('access_token') || '') : ''

  const body: any = {
    content: typeof message === 'string' ? message : message.content
  }
  if (conversationId) body.conversation_id = conversationId
  if (history && history.length) body.history = history

  // DEBUG: log do payload
  console.log('📤 sendMessage -> POST', `${API_BASE}/chat`, 'body=', body)

  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(body)
    })

    // Lança erro para status não OK
    if (!response.ok) {
      const text = await response.text()
      throw new Error(`HTTP ${response.status}: ${text}`)
    }

    const data = await response.json()
    console.log('📡 /chat status:', response.status)
    return data
  } catch (error) {
    console.error('❌ Exceção sendMessage:', error)
    throw error
  }
}