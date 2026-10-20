import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import EvolutionEngine from './EvolutionEngine'

describe('EvolutionEngine', () => {
  it('renders evolution engine component with enhanced features', () => {
    render(<EvolutionEngine />)
    expect(screen.getByText('🧬 AI Evolution Engine')).toBeInTheDocument()
  })

  it('displays engine status section', () => {
    render(<EvolutionEngine />)
    expect(screen.getByText('Engine Status')).toBeInTheDocument()
    expect(screen.getByText(/Status:/)).toBeInTheDocument()
    expect(screen.getByText(/Current Cycle:/)).toBeInTheDocument()
    expect(screen.getByText(/Efficiency:/)).toBeInTheDocument()
  })

  it('shows seed growth metrics', () => {
    render(<EvolutionEngine />)
    expect(screen.getByText('Seed Growth Metrics')).toBeInTheDocument()
    expect(screen.getByText('🌱 Seed Maturity')).toBeInTheDocument()
    expect(screen.getByText('🌿 Branches')).toBeInTheDocument()
    expect(screen.getByText('🍃 Leaf Density')).toBeInTheDocument()
    expect(screen.getByText('🪴 Root Depth')).toBeInTheDocument()
  })

  it('displays recent evolutions section', () => {
    render(<EvolutionEngine />)
    expect(screen.getByText('Recent Evolutions')).toBeInTheDocument()
    expect(screen.getByText('Optimized build path efficiency')).toBeInTheDocument()
    expect(screen.getByText('Enhanced testing patterns')).toBeInTheDocument()
  })

  it('shows evolution controls panel', () => {
    render(<EvolutionEngine />)
    expect(screen.getByText('Evolution Controls')).toBeInTheDocument()
    expect(screen.getByText('🚀 Start Evolution Cycle')).toBeInTheDocument()
    expect(screen.getByText('⏸️ Pause Engine')).toBeInTheDocument()
    expect(screen.getByText('📊 Detailed Analytics')).toBeInTheDocument()
    expect(screen.getByText('🎯 Set Growth Targets')).toBeInTheDocument()
  })

  it('displays growth insights section', () => {
    render(<EvolutionEngine />)
    expect(screen.getByText('Growth Insights')).toBeInTheDocument()
    expect(screen.getByText('🎯 Next Growth Phase')).toBeInTheDocument()
    expect(screen.getByText('⚡ Optimization Opportunities')).toBeInTheDocument()
    expect(screen.getByText('🔍 Health Indicators')).toBeInTheDocument()
  })

  it('shows growth stage indicator', () => {
    render(<EvolutionEngine />)
    // Should show mature stage since seedMaturity is 78%
    expect(screen.getByText('🌲 Mature')).toBeInTheDocument()
    expect(screen.getByText(/% Mature/)).toBeInTheDocument()
  })
})