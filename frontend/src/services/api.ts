import axios, { AxiosInstance, AxiosResponse } from 'axios';
import {
  Metric,
  Anomaly,
  DataSource,
  LogEntry,
  CICDPipeline,
  TestResult,
  AnalyticsSummary,
  QueryRequest,
  QueryResponse,
  HealthResponse,
  AuthResponse,
  TimeSeriesData,
  ConversationalQueryRequest,
  ConversationalQueryResponse
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle errors
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.token = null;
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );

    // Load token from localStorage
    this.token = localStorage.getItem('auth_token');
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  // Authentication
  async login(): Promise<AuthResponse> {
    const response: AxiosResponse<AuthResponse> = await this.client.post('/auth/login');
    this.setToken(response.data.access_token);
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<HealthResponse> {
    const response: AxiosResponse<HealthResponse> = await this.client.get('/health');
    return response.data;
  }

  // Metrics
  async getMetrics(params?: {
    start_time?: string;
    end_time?: string;
    metric_type?: string;
  }): Promise<Metric[]> {
    const response: AxiosResponse<Metric[]> = await this.client.get('/metrics', { params });
    return response.data;
  }

  async ingestMetrics(metricData: any): Promise<{ status: string; ingested_count: number }> {
    const response = await this.client.post('/metrics/ingest', metricData);
    return response.data;
  }

  async getTimeSeriesData(
    metricName: string,
    timeRange: string = '24h',
    aggregation: string = 'avg'
  ): Promise<TimeSeriesData[]> {
    const response = await this.client.get('/metrics/timeseries', {
      params: {
        metric_name: metricName,
        time_range: timeRange,
        aggregation: aggregation,
      },
    });
    return response.data;
  }

  // Anomalies
  async getAnomalies(params?: {
    start_time?: string;
    end_time?: string;
    severity?: string;
  }): Promise<Anomaly[]> {
    const response: AxiosResponse<Anomaly[]> = await this.client.get('/anomalies', { params });
    return response.data;
  }

  async detectAnomalies(metricData: any): Promise<{ anomalies: Anomaly[]; count: number }> {
    const response = await this.client.post('/anomalies/detect', metricData);
    return response.data;
  }

  async resolveAnomaly(anomalyId: number): Promise<boolean> {
    await this.client.post(`/anomalies/${anomalyId}/resolve`);
    return true;
  }

  // Data Sources
  async getDataSources(): Promise<DataSource[]> {
    const response: AxiosResponse<DataSource[]> = await this.client.get('/data-sources');
    return response.data;
  }

  async createDataSource(dataSource: Partial<DataSource>): Promise<DataSource> {
    const response: AxiosResponse<DataSource> = await this.client.post('/data-sources', dataSource);
    return response.data;
  }

  async updateDataSource(id: number, dataSource: Partial<DataSource>): Promise<DataSource> {
    const response: AxiosResponse<DataSource> = await this.client.put(`/data-sources/${id}`, dataSource);
    return response.data;
  }

  async deleteDataSource(id: number): Promise<void> {
    await this.client.delete(`/data-sources/${id}`);
  }

  // Logs
  async getLogEntries(params?: {
    start_time?: string;
    end_time?: string;
    level?: string;
    source?: string;
    limit?: number;
  }): Promise<LogEntry[]> {
    const response: AxiosResponse<LogEntry[]> = await this.client.get('/logs', { params });
    return response.data;
  }

  async ingestLogEntries(logData: any): Promise<{ status: string; ingested_count: number }> {
    const response = await this.client.post('/logs/ingest', logData);
    return response.data;
  }

  // CI/CD Pipelines
  async getCICDPipelines(params?: {
    start_time?: string;
    end_time?: string;
    status?: string;
    limit?: number;
  }): Promise<CICDPipeline[]> {
    const response: AxiosResponse<CICDPipeline[]> = await this.client.get('/cicd/pipelines', { params });
    return response.data;
  }

  async ingestCICDPipeline(pipelineData: any): Promise<CICDPipeline> {
    const response: AxiosResponse<CICDPipeline> = await this.client.post('/cicd/pipelines', pipelineData);
    return response.data;
  }

  // Test Results
  async getTestResults(params?: {
    start_time?: string;
    end_time?: string;
    status?: string;
    test_suite?: string;
    limit?: number;
  }): Promise<TestResult[]> {
    const response: AxiosResponse<TestResult[]> = await this.client.get('/tests/results', { params });
    return response.data;
  }

  async ingestTestResults(testData: any): Promise<{ status: string; ingested_count: number }> {
    const response = await this.client.post('/tests/ingest', testData);
    return response.data;
  }

  // Analytics
  async getAnalyticsSummary(timeRange: string = '24h'): Promise<AnalyticsSummary> {
    const response: AxiosResponse<AnalyticsSummary> = await this.client.get('/analytics/summary', {
      params: { time_range: timeRange },
    });
    return response.data;
  }

  async executeQuery(query: QueryRequest): Promise<QueryResponse> {
    const response: AxiosResponse<QueryResponse> = await this.client.post('/analytics/query', query);
    return response.data;
  }

  // Reports
  async getReports(params?: {
    start_time?: string;
    end_time?: string;
    report_type?: string;
    limit?: number;
  }): Promise<any[]> {
    const response = await this.client.get('/reports', { params });
    return response.data;
  }

  async generateReport(reportData: any): Promise<any> {
    const response = await this.client.post('/reports/generate', reportData);
    return response.data;
  }

  // AI Agents
  async processConversationalQuery(query: ConversationalQueryRequest): Promise<ConversationalQueryResponse> {
    const response: AxiosResponse<ConversationalQueryResponse> = await this.client.post('/ai-agents/conversational-query', query);
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService;
