import { useQuery } from '@tanstack/react-query'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Activity, GitBranch, Brain, Container } from 'lucide-react'

const Dashboard = () => {
  // Fetch system metrics
  const { data: metrics, isLoading } = useQuery({
    queryKey: ['system-metrics'],
    queryFn: async () => {
      try {
        const response = await fetch('/api/metrics')
        if (!response.ok) {
          throw new Error('Failed to fetch metrics')
        }
        return await response.json()
      } catch (error) {
        // Return mock data for development
        return {
          paths: {
            total: 12,
            active: 8,
            optimized: 5
          },
          evolution: {
            cycles: 23,
            improvements: 47,
            efficiency: 94.2
          },
          system: {
            uptime: '2d 14h 23m',
            cpu: 23.5,
            memory: 67.8,
            containers: 6
          }
        }
      }
    },
    refetchInterval: 5000, // Refresh every 5 seconds
  })

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '2rem' }}>
        <Activity className="animate-spin" size={48} style={{ margin: '0 auto 1rem' }} />
        <p>Loading AI-Seed dashboard...</p>
      </div>
    )
  }

  const pathData = [
    { name: 'Build', efficiency: 98 },
    { name: 'Test', efficiency: 95 },
    { name: 'Deploy', efficiency: 92 },
    { name: 'Monitor', efficiency: 97 },
    { name: 'Evolution', efficiency: 89 },
  ]

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
      <header style={{ marginBottom: '2rem', textAlign: 'left' }}>
        <h1 style={{ fontSize: '2.5rem', margin: '0 0 0.5rem 0' }}>
          🌱 AI-Seed Dashboard
        </h1>
        <p style={{ fontSize: '1.1rem', opacity: 0.8 }}>
          Monitor your evolving development ecosystem
        </p>
      </header>

      {/* Metrics Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '1.5rem',
        marginBottom: '2rem'
      }}>
        <MetricCard
          icon={<GitBranch size={24} />}
          title="Active Paths"
          value={metrics?.paths?.active || 0}
          subtitle={`${metrics?.paths?.total || 0} total paths`}
          color="#4ade80"
        />
        
        <MetricCard
          icon={<Brain size={24} />}
          title="Evolution Cycles"
          value={metrics?.evolution?.cycles || 0}
          subtitle={`${metrics?.evolution?.improvements || 0} improvements`}
          color="#8b5cf6"
        />
        
        <MetricCard
          icon={<Container size={24} />}
          title="System Health"
          value={`${metrics?.evolution?.efficiency || 0}%`}
          subtitle={`${metrics?.system?.containers || 0} containers`}
          color="#06b6d4"
        />
        
        <MetricCard
          icon={<Activity size={24} />}
          title="Uptime"
          value={metrics?.system?.uptime || '0h'}
          subtitle={`CPU: ${metrics?.system?.cpu || 0}%`}
          color="#f59e0b"
        />
      </div>

      {/* Path Efficiency Chart */}
      <div className="path-visualization">
        <h2 style={{ marginBottom: '1rem' }}>Path Efficiency Metrics</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={pathData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="efficiency" fill="#4ade80" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Recent Activity */}
      <div className="path-visualization" style={{ marginTop: '1.5rem' }}>
        <h2 style={{ marginBottom: '1rem' }}>Recent Evolution Activity</h2>
        <div style={{ textAlign: 'left' }}>
          <ActivityItem
            time="2 minutes ago"
            action="Optimized build path efficiency by 12%"
            type="improvement"
          />
          <ActivityItem
            time="15 minutes ago"
            action="New test path discovered and integrated"
            type="discovery"
          />
          <ActivityItem
            time="1 hour ago"
            action="Deployment path auto-healing completed"
            type="healing"
          />
          <ActivityItem
            time="3 hours ago"
            action="Evolution cycle #23 completed successfully"
            type="cycle"
          />
        </div>
      </div>
    </div>
  )
}

const MetricCard = ({ icon, title, value, subtitle, color }) => (
  <div className="path-visualization" style={{ textAlign: 'left' }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
      <span style={{ color }}>{icon}</span>
      <h3 style={{ margin: 0, fontSize: '1rem' }}>{title}</h3>
    </div>
    <div style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0.5rem 0' }}>
      {value}
    </div>
    <div style={{ fontSize: '0.9rem', opacity: 0.7 }}>
      {subtitle}
    </div>
  </div>
)

const ActivityItem = ({ time, action, type }) => {
  const getIcon = () => {
    switch (type) {
      case 'improvement': return '⚡'
      case 'discovery': return '🔍'
      case 'healing': return '🛠️'
      case 'cycle': return '🔄'
      default: return '📝'
    }
  }

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '1rem',
      padding: '0.75rem 0',
      borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
    }}>
      <span style={{ fontSize: '1.2rem' }}>{getIcon()}</span>
      <div style={{ flex: 1 }}>
        <div>{action}</div>
        <div style={{ fontSize: '0.8rem', opacity: 0.6 }}>{time}</div>
      </div>
    </div>
  )
}

export default Dashboard