import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Sprout, Brain, Container, Activity } from 'lucide-react'
import Dashboard from './components/Dashboard'
import PathVisualization from './components/PathVisualization'
import EvolutionEngine from './components/EvolutionEngine'
import SystemHealth from './components/SystemHealth'
import Navigation from './components/Navigation'

function App() {
  return (
    <div className="seed-container">
      <Navigation />
      <main style={{ flex: 1, padding: '20px' }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/paths" element={<PathVisualization />} />
          <Route path="/evolution" element={<EvolutionEngine />} />
          <Route path="/health" element={<SystemHealth />} />
        </Routes>
      </main>
    </div>
  )
}

export default App