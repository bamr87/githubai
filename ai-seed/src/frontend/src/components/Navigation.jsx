import { Link, useLocation } from 'react-router-dom'
import { Sprout, Activity, Brain, GitBranch, Home } from 'lucide-react'

const Navigation = () => {
  const location = useLocation()

  const navItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/paths', icon: GitBranch, label: 'Paths' },
    { path: '/evolution', icon: Brain, label: 'Evolution' },
    { path: '/health', icon: Activity, label: 'Health' },
  ]

  return (
    <nav style={{
      background: 'rgba(255, 255, 255, 0.1)',
      backdropFilter: 'blur(10px)',
      padding: '1rem 2rem',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      borderBottom: '1px solid rgba(255, 255, 255, 0.2)'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Sprout size={32} color="#4ade80" />
        <h1 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 'bold' }}>
          AI-Seed
        </h1>
      </div>
      
      <div style={{ display: 'flex', gap: '1rem' }}>
        {navItems.map(({ path, icon: Icon, label }) => (
          <Link
            key={path}
            to={path}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.5rem 1rem',
              borderRadius: '8px',
              textDecoration: 'none',
              color: 'inherit',
              background: location.pathname === path ? 'rgba(255, 255, 255, 0.2)' : 'transparent',
              transition: 'background 0.2s'
            }}
          >
            <Icon size={18} />
            {label}
          </Link>
        ))}
      </div>
    </nav>
  )
}

export default Navigation