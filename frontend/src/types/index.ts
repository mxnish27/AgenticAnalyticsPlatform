export interface Metric {
  id: number;
  name: string;
  value: number;
  unit?: string;
  source: string;
  timestamp: string;
  tags?: Record<string, any>;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface Anomaly {
  id: number;
  metric_id: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  score: number;
  description: string;
  detected_at: string;
  resolved: boolean;
  resolved_at?: string;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface DataSource {
  id: number;
  name: string;
  type: 'logs' | 'metrics' | 'cicd' | 'tests';
  config: Record<string, any>;
  enabled: boolean;
  last_sync?: string;
  created_at: string;
  updated_at?: string;
}

export interface LogEntry {
  id: number;
  level: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR' | 'FATAL';
  message: string;
  source: string;
  timestamp: string;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface CICDPipeline {
  id: number;
  pipeline_name: string;
  status: 'success' | 'failed' | 'running' | 'pending';
  duration?: number;
  start_time?: string;
  end_time?: string;
  commit_hash?: string;
  branch?: string;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface TestResult {
  id: number;
  test_suite: string;
  test_name: string;
  status: 'passed' | 'failed' | 'skipped';
  duration?: number;
  error_message?: string;
  timestamp: string;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface AnalyticsSummary {
  total_metrics: number;
  total_anomalies: number;
  active_data_sources: number;
  recent_pipelines: number;
  test_pass_rate: number;
  time_range: string;
  generated_at: string;
}

export interface QueryRequest {
  query: string;
  time_range?: string;
  filters?: Record<string, any>;
}

export interface QueryResponse {
  results: Record<string, any>[];
  metadata: {
    query_type: string;
    time_range: string;
    result_count: number;
    execution_time: number;
  };
  execution_time: number;
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface TimeSeriesData {
  timestamp: string;
  value: number | null;
}

export interface DashboardWidget {
  id: string;
  type: 'metric' | 'chart' | 'table' | 'anomaly' | 'log';
  title: string;
  size: 'small' | 'medium' | 'large';
  data: any;
  config?: Record<string, any>;
}

export interface DashboardLayout {
  widgets: DashboardWidget[];
  layout: {
    [key: string]: {
      x: number;
      y: number;
      w: number;
      h: number;
    };
  };
}

export interface ConversationalQueryRequest {
  query: string;
  context?: {
    previous_messages?: any[];
    timestamp?: string;
  };
}

export interface ConversationalQueryResponse {
  result: {
    response: string;
    insights?: any[];
    data?: any;
  };
  metadata: {
    processing_time: number;
    confidence: number;
    model_used: string;
  };
}
