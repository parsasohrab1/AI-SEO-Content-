import type { Metadata } from 'next'
import './globals.css'
import { ErrorBoundary } from './error-boundary'
import { ErrorSuppressor } from './components/ErrorSuppressor'

export const metadata: Metadata = {
  title: 'AI Content Factory Pro',
  description: 'سیستم تولید و بهینه‌سازی محتوای خودکار',
  icons: {
    icon: '/icon.svg',
    shortcut: '/icon.svg',
    apple: '/icon.svg',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fa" dir="rtl">
      <body suppressHydrationWarning>
        <ErrorSuppressor />
        <ErrorBoundary>
          {children}
        </ErrorBoundary>
      </body>
    </html>
  )
}

