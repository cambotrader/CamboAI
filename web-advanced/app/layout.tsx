import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { ThemeProvider } from '@/components/theme-provider'
import { QueryProvider } from '@/components/query-provider'
import { Toaster } from '@/components/ui/toaster'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'CamboAI - Unified Trading Platform',
  description: 'Advanced AI-powered trading intelligence platform combining all CamboStation projects',
  keywords: 'trading, AI, CamboAI, CamboStation, quantitative trading, market analysis',
  authors: [{ name: 'CamboAI Team' }],
  viewport: 'width=device-width, initial-scale=1',
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#1976d2' },
    { media: '(prefers-color-scheme: dark)', color: '#42a5f5' },
  ],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="CamboAI" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="msapplication-TileColor" content="#1976d2" />
        <meta name="theme-color" content="#1976d2" />
        <style dangerouslySetInnerHTML={{
          __html: `
            /* Prevent browser extension interference */
            .translate-tooltip-mtz,
            .translate-tooltip,
            [class*="translate"],
            [class*="extension"],
            [hidden="null"] {
              display: none !important;
              visibility: hidden !important;
              opacity: 0 !important;
            }
            
            /* Prevent hydration flash */
            body { 
              visibility: hidden; 
              opacity: 0;
              transition: opacity 0.3s ease;
            }
            body.hydrated { 
              visibility: visible; 
              opacity: 1;
            }
          `
        }} />
      </head>
      <body className={inter.className} suppressHydrationWarning>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <QueryProvider>
            <div className="min-h-screen bg-background">
              {children}
            </div>
            <Toaster />
          </QueryProvider>
        </ThemeProvider>
        <script dangerouslySetInnerHTML={{
          __html: `
            setTimeout(() => {
              document.body.classList.add('hydrated');
            }, 100);
          `
        }} />
      </body>
    </html>
  )
}