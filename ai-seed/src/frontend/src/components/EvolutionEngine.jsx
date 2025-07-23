import { useState, useEffect } from 'react';
import './EvolutionEngine.css';

/**
 * Enhanced EvolutionEngine component representing seed growth and evolution
 * Features real-time metrics, growth tracking, and advanced evolution controls
 */
const EvolutionEngine = () => {
  const [engineState, setEngineState] = useState({
    status: 'Running',
    currentCycle: 23,
    efficiency: 94.2,
    isEvolving: false
  });

  const [growthMetrics, setGrowthMetrics] = useState({
    seedMaturity: 78,
    branchCount: 12,
    leafDensity: 156,
    rootDepth: 45
  });

  const [recentEvolutions, setRecentEvolutions] = useState([
    { id: 1, type: 'optimization', description: 'Optimized build path efficiency', impact: 'high', timestamp: '2 mins ago' },
    { id: 2, type: 'enhancement', description: 'Enhanced testing patterns', impact: 'medium', timestamp: '5 mins ago' },
    { id: 3, type: 'security', description: 'Security configuration updates', impact: 'high', timestamp: '8 mins ago' },
    { id: 4, type: 'documentation', description: 'Documentation improvements', impact: 'low', timestamp: '12 mins ago' }
  ]);

  useEffect(() => {
    // Simulate real-time updates for seed growth
    const interval = setInterval(() => {
      setGrowthMetrics(prev => ({
        ...prev,
        seedMaturity: Math.min(100, prev.seedMaturity + Math.random() * 0.5),
        leafDensity: prev.leafDensity + Math.floor(Math.random() * 3)
      }));
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const startEvolutionCycle = () => {
    setEngineState(prev => ({ ...prev, isEvolving: true }));
    
    setTimeout(() => {
      setEngineState(prev => ({
        ...prev,
        currentCycle: prev.currentCycle + 1,
        efficiency: Math.min(100, prev.efficiency + Math.random() * 2),
        isEvolving: false
      }));
      
      // Add new evolution to the list
      const newEvolution = {
        id: Date.now(),
        type: 'growth',
        description: 'Seed growth cycle completed - new capabilities emerged',
        impact: 'high',
        timestamp: 'just now'
      };
      
      setRecentEvolutions(prev => [newEvolution, ...prev.slice(0, 3)]);
    }, 2000);
  };

  const getGrowthStage = (maturity) => {
    if (maturity < 25) return '🌱 Seedling';
    if (maturity < 50) return '🌿 Sprouting';
    if (maturity < 75) return '🌳 Growing';
    return '🌲 Mature';
  };

  const getImpactIcon = (impact) => {
    switch (impact) {
      case 'high': return '🔥';
      case 'medium': return '⚡';
      case 'low': return '💡';
      default: return '📝';
    }
  };

  return (
    <div className="evolution-engine">
      <div className="engine-header">
        <h2>🧬 AI Evolution Engine</h2>
        <div className="growth-stage">
          <span className="stage-indicator">{getGrowthStage(growthMetrics.seedMaturity)}</span>
          <span className="maturity-score">{growthMetrics.seedMaturity.toFixed(1)}% Mature</span>
        </div>
      </div>

      <div className="engine-grid">
        <div className="engine-status">
          <h3>Engine Status</h3>
          <div className="status-indicator">
            <span className={`status-dot ${engineState.status.toLowerCase()}`}></span>
            <p>Status: {engineState.status}</p>
          </div>
          <p>Current Cycle: {engineState.currentCycle}</p>
          <p>Efficiency: {engineState.efficiency.toFixed(1)}%</p>
          {engineState.isEvolving && (
            <div className="evolution-progress">
              <p>🔄 Evolution in progress...</p>
              <div className="progress-bar">
                <div className="progress-fill"></div>
              </div>
            </div>
          )}
        </div>

        <div className="growth-metrics">
          <h3>Seed Growth Metrics</h3>
          <div className="metrics-grid">
            <div className="metric">
              <span className="metric-label">🌱 Seed Maturity</span>
              <span className="metric-value">{growthMetrics.seedMaturity.toFixed(1)}%</span>
            </div>
            <div className="metric">
              <span className="metric-label">🌿 Branches</span>
              <span className="metric-value">{growthMetrics.branchCount}</span>
            </div>
            <div className="metric">
              <span className="metric-label">🍃 Leaf Density</span>
              <span className="metric-value">{growthMetrics.leafDensity}</span>
            </div>
            <div className="metric">
              <span className="metric-label">🪴 Root Depth</span>
              <span className="metric-value">{growthMetrics.rootDepth}m</span>
            </div>
          </div>
        </div>

        <div className="recent-evolutions">
          <h3>Recent Evolutions</h3>
          <ul className="evolution-list">
            {recentEvolutions.map((evolution) => (
              <li key={evolution.id} className="evolution-item">
                <span className="evolution-icon">{getImpactIcon(evolution.impact)}</span>
                <div className="evolution-content">
                  <p className="evolution-description">{evolution.description}</p>
                  <span className="evolution-meta">
                    <span className={`impact ${evolution.impact}`}>{evolution.impact}</span>
                    • {evolution.timestamp}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        </div>

        <div className="control-panel">
          <h3>Evolution Controls</h3>
          <button 
            className="evolution-button primary"
            onClick={startEvolutionCycle}
            disabled={engineState.isEvolving}
          >
            {engineState.isEvolving ? '🔄 Evolving...' : '🚀 Start Evolution Cycle'}
          </button>
          <button className="evolution-button secondary">
            ⏸️ Pause Engine
          </button>
          <button className="evolution-button secondary">
            📊 Detailed Analytics
          </button>
          <button className="evolution-button secondary">
            🎯 Set Growth Targets
          </button>
        </div>
      </div>

      <div className="evolution-insights">
        <h3>Growth Insights</h3>
        <div className="insights-grid">
          <div className="insight-card">
            <h4>🎯 Next Growth Phase</h4>
            <p>Based on current metrics, the seed is ready for advanced branching patterns and deeper root exploration.</p>
          </div>
          <div className="insight-card">
            <h4>⚡ Optimization Opportunities</h4>
            <p>Test coverage expansion could accelerate growth by 15%. Consider adding integration tests for new branches.</p>
          </div>
          <div className="insight-card">
            <h4>🔍 Health Indicators</h4>
            <p>All systems showing positive growth trends. Recommend maintaining current evolution pace.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EvolutionEngine;