-- AI-Seed Database Initialization Script
-- Path: Database Setup → Schema Creation → Initial Data → Path Monitoring Tables

-- Create database (this will be run by docker-entrypoint-initdb.d)
-- The database is already created by the environment variables

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create schema for AI-Seed
CREATE SCHEMA IF NOT EXISTS ai_seed;

-- Set search path
SET search_path TO ai_seed, public;

-- Path execution tracking table
CREATE TABLE paths (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    steps JSONB NOT NULL DEFAULT '[]',
    status VARCHAR(50) DEFAULT 'active',
    efficiency DECIMAL(5,2) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Path execution history
CREATE TABLE path_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    path_id UUID REFERENCES paths(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL, -- running, completed, failed
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP WITH TIME ZONE,
    duration_ms INTEGER,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Evolution cycles tracking
CREATE TABLE evolution_cycles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cycle_number INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL, -- running, completed, failed
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP WITH TIME ZONE,
    improvements_count INTEGER DEFAULT 0,
    paths_affected JSONB DEFAULT '[]',
    metrics JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- System metrics tracking
CREATE TABLE system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(255) NOT NULL,
    metric_value DECIMAL(10,4) NOT NULL,
    metric_unit VARCHAR(50),
    tags JSONB DEFAULT '{}',
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- AI suggestions and recommendations
CREATE TABLE ai_suggestions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    suggestion_type VARCHAR(100) NOT NULL, -- performance, reliability, security, etc.
    priority VARCHAR(50) DEFAULT 'medium', -- low, medium, high, critical
    complexity VARCHAR(50) DEFAULT 'medium', -- low, medium, high
    estimated_impact TEXT,
    estimated_time VARCHAR(100),
    paths_affected JSONB DEFAULT '[]',
    status VARCHAR(50) DEFAULT 'pending', -- pending, approved, applied, rejected
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    applied_at TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(255) DEFAULT 'ai-engine'
);

-- Create indexes for better performance
CREATE INDEX idx_paths_status ON paths(status);
CREATE INDEX idx_paths_efficiency ON paths(efficiency DESC);
CREATE INDEX idx_path_executions_path_id ON path_executions(path_id);
CREATE INDEX idx_path_executions_status ON path_executions(status);
CREATE INDEX idx_path_executions_start_time ON path_executions(start_time DESC);
CREATE INDEX idx_evolution_cycles_cycle_number ON evolution_cycles(cycle_number DESC);
CREATE INDEX idx_system_metrics_name_time ON system_metrics(metric_name, recorded_at DESC);
CREATE INDEX idx_ai_suggestions_status ON ai_suggestions(status);
CREATE INDEX idx_ai_suggestions_priority ON ai_suggestions(priority);

-- Insert initial path data
INSERT INTO paths (name, description, steps, status, efficiency) VALUES
('build-path', 'Code compilation and artifact generation', 
 '["Source Code", "Dependencies", "Compilation", "Artifacts"]', 'active', 98.0),

('test-path', 'Automated testing and quality assurance', 
 '["Unit Tests", "Integration", "E2E Tests", "Coverage"]', 'active', 95.0),

('deploy-path', 'Application deployment and release', 
 '["Package", "Staging", "Validation", "Production"]', 'active', 87.0),

('evolution-path', 'AI-powered optimization and improvement', 
 '["Analysis", "Planning", "Implementation", "Validation"]', 'active', 92.0),

('monitor-path', 'System health and performance monitoring', 
 '["Metrics", "Alerts", "Analysis", "Response"]', 'active', 97.0);

-- Insert sample evolution cycle
INSERT INTO evolution_cycles (cycle_number, status, improvements_count, paths_affected, metrics) VALUES
(23, 'completed', 5, '["build-path", "test-path", "deploy-path"]', 
 '{"efficiency_gain": 12.5, "time_saved_seconds": 450, "reliability_improvement": 8.3}');

-- Insert sample AI suggestions
INSERT INTO ai_suggestions (title, description, suggestion_type, priority, complexity, estimated_impact, estimated_time, paths_affected) VALUES
('Optimize Container Build Cache', 
 'Implement multi-stage Docker builds with better layer caching for faster builds', 
 'performance', 'high', 'medium', 'Build time reduction: 30-40%', '2-3 hours', 
 '["build-path"]'),

('Add Circuit Breaker Pattern', 
 'Implement circuit breakers for external API calls to improve reliability', 
 'reliability', 'medium', 'low', 'Error rate reduction: 25%', '1-2 hours', 
 '["api-path"]'),

('Implement Horizontal Pod Autoscaling', 
 'Add automatic scaling based on CPU and memory usage for better resource utilization', 
 'scalability', 'low', 'high', 'Better resource utilization and cost optimization', '4-6 hours', 
 '["deploy-path", "monitor-path"]');

-- Insert sample system metrics
INSERT INTO system_metrics (metric_name, metric_value, metric_unit, tags) VALUES
('cpu_usage_percent', 23.5, 'percent', '{"service": "api", "environment": "development"}'),
('memory_usage_percent', 67.8, 'percent', '{"service": "api", "environment": "development"}'),
('response_time_ms', 120, 'milliseconds', '{"service": "api", "endpoint": "/health"}'),
('path_efficiency', 98.0, 'percent', '{"path": "build-path"}'),
('path_efficiency', 95.0, 'percent', '{"path": "test-path"}'),
('path_efficiency', 87.0, 'percent', '{"path": "deploy-path"}');

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for automatic timestamp updates
CREATE TRIGGER update_paths_updated_at BEFORE UPDATE ON paths
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create view for path summary with latest metrics
CREATE VIEW path_summary AS
SELECT 
    p.id,
    p.name,
    p.description,
    p.status,
    p.efficiency,
    COUNT(pe.id) as total_executions,
    MAX(pe.start_time) as last_execution,
    AVG(pe.duration_ms) as avg_duration_ms,
    SUM(CASE WHEN pe.status = 'failed' THEN 1 ELSE 0 END)::DECIMAL / COUNT(pe.id) * 100 as error_rate
FROM paths p
LEFT JOIN path_executions pe ON p.id = pe.path_id
GROUP BY p.id, p.name, p.description, p.status, p.efficiency;

-- Grant permissions (adjust as needed for your security requirements)
-- In production, you would create specific users with limited permissions
GRANT ALL ON SCHEMA ai_seed TO PUBLIC;
GRANT ALL ON ALL TABLES IN SCHEMA ai_seed TO PUBLIC;
GRANT ALL ON ALL SEQUENCES IN SCHEMA ai_seed TO PUBLIC;

-- Insert a comment about the initialization
COMMENT ON SCHEMA ai_seed IS 'AI-Seed database schema for path-based development and evolution tracking';

-- Log the successful initialization
INSERT INTO system_metrics (metric_name, metric_value, metric_unit, tags) VALUES
('database_initialized', 1, 'boolean', '{"event": "database_setup", "timestamp": "' || CURRENT_TIMESTAMP || '"}');

-- Show summary of created objects
SELECT 
    'Tables created: ' || count(*) as summary
FROM information_schema.tables 
WHERE table_schema = 'ai_seed';

-- Log success message
DO $$
BEGIN
    RAISE NOTICE '🌱 AI-Seed database initialized successfully!';
    RAISE NOTICE '📊 Schema: ai_seed';
    RAISE NOTICE '🛤️ Tables: paths, path_executions, evolution_cycles, system_metrics, ai_suggestions';
    RAISE NOTICE '📈 Views: path_summary';
    RAISE NOTICE '🔍 Ready for path-based development!';
END $$;