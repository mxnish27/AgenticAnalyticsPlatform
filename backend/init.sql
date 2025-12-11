-- Initialize database extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics(name);
CREATE INDEX IF NOT EXISTS idx_metrics_source ON metrics(source);
CREATE INDEX IF NOT EXISTS idx_anomalies_detected_at ON anomalies(detected_at);
CREATE INDEX IF NOT EXISTS idx_anomalies_severity ON anomalies(severity);
CREATE INDEX IF NOT EXISTS idx_log_entries_timestamp ON log_entries(timestamp);
CREATE INDEX IF NOT EXISTS idx_log_entries_level ON log_entries(level);
CREATE INDEX IF NOT EXISTS idx_cicd_pipelines_created_at ON cicd_pipelines(created_at);
CREATE INDEX IF NOT EXISTS idx_test_results_timestamp ON test_results(timestamp);

-- Create sample data for testing
INSERT INTO data_sources (name, type, config, enabled) VALUES
('application_logs', 'logs', '{"path": "/var/log/app.log", "format": "json"}', true),
('prometheus_metrics', 'metrics', '{"url": "http://prometheus:9090", "scrape_interval": "15s"}', true),
('github_actions', 'cicd', '{"repo": "analytics-platform", "token": "github_token"}', true),
('pytest_results', 'tests', '{"path": "/test-results", "format": "junit"}', true);

-- Insert sample metrics
INSERT INTO metrics (name, value, unit, source, tags, metadata) VALUES
('cpu_usage', 75.5, 'percent', 'prometheus', '{"instance": "server1", "job": "node"}', '{"region": "us-east-1"}'),
('memory_usage', 68.2, 'percent', 'prometheus', '{"instance": "server1", "job": "node"}', '{"region": "us-east-1"}'),
('response_time', 245.8, 'milliseconds', 'application', '{"endpoint": "/api/metrics", "method": "GET"}', '{"version": "v1"}'),
('error_rate', 2.1, 'percent', 'application', '{"service": "api-gateway"}', '{"environment": "production"}'),
('throughput', 1250.0, 'requests_per_second', 'load_balancer', '{"pool": "api-servers"}', '{"datacenter": "dc1"}');

-- Insert sample log entries
INSERT INTO log_entries (level, message, source, metadata) VALUES
('INFO', 'Application started successfully', 'application', '{"pid": 1234, "version": "1.0.0"}'),
('WARN', 'High memory usage detected', 'monitoring', '{"usage": "85%", "threshold": "80%"}'),
('ERROR', 'Database connection failed', 'database', '{"error": "timeout", "retry_count": 3}'),
('INFO', 'User authentication successful', 'auth', '{"user_id": "user123", "ip": "192.168.1.100"}'),
('ERROR', 'API request failed', 'api', '{"endpoint": "/api/analytics", "status_code": 500}');

-- Insert sample CI/CD pipelines
INSERT INTO cicd_pipelines (pipeline_name, status, duration, start_time, end_time, commit_hash, branch, metadata) VALUES
('build-and-test', 'success', 245.5, NOW() - INTERVAL '2 hours', NOW() - INTERVAL '1 hour 55 minutes', 'abc123def', 'main', '{"build_number": 123, "trigger": "push"}'),
('deploy-staging', 'failed', 180.2, NOW() - INTERVAL '4 hours', NOW() - INTERVAL '3 hours 55 minutes', 'def456ghi', 'develop', '{"build_number": 122, "trigger": "manual"}'),
('integration-tests', 'success', 320.8, NOW() - INTERVAL '6 hours', NOW() - INTERVAL '5 hours 35 minutes', 'ghi789jkl', 'feature/new-dashboard', '{"build_number": 121, "trigger": "pull_request"}');

-- Insert sample test results
INSERT INTO test_results (test_suite, test_name, status, duration, error_message, metadata) VALUES
('unit_tests', 'test_metrics_service', 'passed', 2.5, NULL, '{"file": "test_metrics.py", "line": 45}'),
('unit_tests', 'test_anomaly_detection', 'failed', 5.2, 'AssertionError: Expected anomaly count to be 1, got 0', '{"file": "test_anomalies.py", "line": 78}'),
('integration_tests', 'test_api_endpoints', 'passed', 15.8, NULL, '{"file": "test_api.py", "line": 120}'),
('integration_tests', 'test_database_connection', 'passed', 3.1, NULL, '{"file": "test_db.py", "line": 34}'),
('e2e_tests', 'test_dashboard_loading', 'skipped', 0.0, 'Test skipped due to environment limitations', '{"file": "test_e2e.py", "line": 200}');

-- Insert sample user
INSERT INTO users (username, email, hashed_password, is_active, is_admin) VALUES
('admin', 'admin@analytics.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsZYmPnMa', true, true);
