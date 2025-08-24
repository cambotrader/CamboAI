import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { ThemeProvider } from '@/components/theme-provider'
import { QueryProvider } from '@/components/query-provider'
import { Toaster } from '@/components/ui/toaster'
import ErrorBoundary from '@/components/error-boundary'

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
            /* Prevent browser extension interference and persistent popups */
            .translate-tooltip-mtz,
            .translate-tooltip,
            [class*="translate"],
            [class*="extension"],
            [class*="popup"],
            [class*="modal"],
            [class*="notification"],
            [class*="toast"]:not([data-camboai]),
            [hidden="null"],
            [data-extension],
            [data-popup],
            div[style*="position: fixed"]:not([data-camboai]) {
              display: none !important;
              visibility: hidden !important;
              opacity: 0 !important;
              pointer-events: none !important;
              z-index: -9999 !important;
            }
            
            /* Specifically target model change popups */
            *[class*="model"]:not([data-camboai]),
            *[id*="model"]:not([data-camboai]),
            div:contains("Model can't be changed"),
            div:contains("model"),
            div:contains("chat") {
              display: none !important;
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
        <ErrorBoundary>
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
        </ErrorBoundary>
        <script dangerouslySetInnerHTML={{
          __html: `
            // Prevent persistent popups and notifications
            let popupCount = 0;
            const maxPopups = 3;
            
            // Override alert, confirm, and prompt to prevent spam
            const originalAlert = window.alert;
            const originalConfirm = window.confirm;
            const originalPrompt = window.prompt;
            
            window.alert = function(message) {
              if (popupCount >= maxPopups) {
                console.warn('Too many popups blocked:', message);
                return;
              }
              popupCount++;
              setTimeout(() => popupCount = Math.max(0, popupCount - 1), 5000);
              return originalAlert.call(this, message);
            };
            
            window.confirm = function(message) {
              if (popupCount >= maxPopups) {
                console.warn('Too many popups blocked:', message);
                return false;
              }
              popupCount++;
              setTimeout(() => popupCount = Math.max(0, popupCount - 1), 5000);
              return originalConfirm.call(this, message);
            };
            
            window.prompt = function(message, defaultText) {
              if (popupCount >= maxPopups) {
                console.warn('Too many popups blocked:', message);
                return null;
              }
              popupCount++;
              setTimeout(() => popupCount = Math.max(0, popupCount - 1), 5000);
              return originalPrompt.call(this, message, defaultText);
            };
            
            // Prevent extension interference
            const observer = new MutationObserver((mutations) => {
              mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                  if (node.nodeType === 1) {
                    const element = node;
                    // Remove extension-related elements
                    if (element.className && (
                      element.className.includes('translate') ||
                      element.className.includes('extension') ||
                      element.className.includes('popup')
                    )) {
                      element.remove();
                    }
                  }
                });
              });
            });
            
            observer.observe(document.body, {
              childList: true,
              subtree: true
            });
            
            setTimeout(() => {
              document.body.classList.add('hydrated');
            }, 100);
          `
        }} />
      </body>
    </html>
  )
}