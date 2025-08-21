import type { Metadata, Viewport } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'IFSC Chat - Assistente Virtual',
  description: 'Assistente virtual do Instituto de Física de São Carlos (IFSC-USP)',
  keywords: ['IFSC', 'USP', 'física', 'São Carlos', 'chatbot', 'assistente virtual'],
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR" className="h-full" suppressHydrationWarning>
      <head>
        <link rel="icon" href="/favicon.ico" />
        <meta name="theme-color" content="#2563eb" />
      </head>
      <body className="h-full font-sans antialiased bg-gray-50" suppressHydrationWarning>
        <div id="root" className="h-full">
          {children}
        </div>
      </body>
    </html>
  )
}