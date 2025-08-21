"use client"

import { useEffect, useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'

interface AuthGuardProps {
  children: React.ReactNode
}

export default function AuthGuard({ children }: AuthGuardProps) {
  const [isChecking, setIsChecking] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    const checkAuth = () => {
      try {
        const token = localStorage.getItem('access_token')
        const userData = localStorage.getItem('user_data')
        const isAuth = !!(token && userData)
        
        console.log('🔍 AuthGuard - Verificando autenticação:', { 
          token: !!token, 
          userData: !!userData, 
          isAuth,
          pathname 
        })
        
        setIsAuthenticated(isAuth)
        setIsChecking(false)
        
        // Se não estiver autenticado e não estiver já na página de login
        if (!isAuth && pathname !== '/login') {
          console.log('❌ AuthGuard - Usuário não autenticado, redirecionando para login...')
          router.replace('/login')
        } else if (isAuth) {
          console.log('✅ AuthGuard - Usuário autenticado!')
        }
      } catch (error) {
        console.error('❌ AuthGuard - Erro ao verificar autenticação:', error)
        setIsAuthenticated(false)
        setIsChecking(false)
        if (pathname !== '/login') {
          router.replace('/login')
        }
      }
    }

    // Verificar imediatamente e depois com um pequeno delay
    checkAuth()
    const timeoutId = setTimeout(checkAuth, 100)
    
    return () => clearTimeout(timeoutId)
  }, [router, pathname])

  // Se estiver na página de login, sempre renderizar
  if (pathname === '/login') {
    return <>{children}</>
  }

  // Loading state para outras páginas
  if (isChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg mx-auto mb-4">
            <span className="text-white text-xl font-bold">IFSC</span>
          </div>
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Verificando autenticação...</p>
        </div>
      </div>
    )
  }

  // Se não autenticado, mostrar tela de redirecionamento
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg mx-auto mb-4">
            <span className="text-white text-xl font-bold">IFSC</span>
          </div>
          <p className="text-gray-600">Redirecionando para login...</p>
        </div>
      </div>
    )
  }

  // Se autenticado, renderizar o conteúdo
  return <>{children}</>
}