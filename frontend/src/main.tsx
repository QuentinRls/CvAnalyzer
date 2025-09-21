import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'sonner'
import App from './App'
import { queryClient } from './lib/query.ts'
import './app.css'

// Always hide page scrollbar (global UX decision)
try {
  if (typeof document !== 'undefined' && document.documentElement) {
    document.documentElement.classList.add('hide-scrollbar');
  }
} catch (e) {
  // ignore
}

// Force rebuild - session isolation fix v2.0
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
        <Toaster position="top-right" />
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>,
)
