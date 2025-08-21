interface User {
  username: string
  name: string
  email: string
  role: string
}

export const getAuthToken = (): string | null => {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('access_token')
}

export const getUserData = (): User | null => {
  if (typeof window === 'undefined') return null
  const userData = localStorage.getItem('user_data')
  return userData ? JSON.parse(userData) : null
}

export const isAuthenticated = (): boolean => {
  return !!getAuthToken()
}

export const logout = (): void => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('user_data')
  window.location.href = '/login'
}

export const getAuthHeaders = () => {
  const token = getAuthToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export const redirectToLogin = () => {
  window.location.href = '/login'
}

export const redirectToDashboard = () => {
  window.location.href = '/'
}

export const checkTokenExpiration = () => {
  const token = getAuthToken()
  if (!token) return false

  try {
    // Decode JWT payload (sem verificar assinatura)
    const payload = JSON.parse(atob(token.split('.')[1]))
    const now = Date.now() / 1000
    
    if (payload.exp < now) {
      logout()
      return false
    }
    return true
  } catch {
    logout()
    return false
  }
}