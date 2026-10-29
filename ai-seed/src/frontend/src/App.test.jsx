import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App'

// Create a test query client
const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

// Wrapper component for router and query client context
const AppWithProviders = () => {
  const queryClient = createTestQueryClient()
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  )
}

describe('App', () => {
  it('renders app title', () => {
    render(<AppWithProviders />)
    expect(screen.getByText('AI-Seed')).toBeInTheDocument()
  })

  it('renders navigation', () => {
    render(<AppWithProviders />)
    expect(screen.getByRole('navigation')).toBeInTheDocument()
  })

  it('renders main content area', () => {
    render(<AppWithProviders />)
    expect(screen.getByRole('main')).toBeInTheDocument()
  })
})