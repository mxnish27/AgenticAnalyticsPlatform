import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import {
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ArrowPathIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline';
import { Anomaly } from '../types';
import { apiService } from '../services/api';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const Anomalies: React.FC = () => {
  const [filters, setFilters] = useState({
    start_time: '',
    end_time: '',
    severity: '',
  });

  const queryClient = useQueryClient();

  const { data: anomalies, isLoading, error } = useQuery(
    ['anomalies', filters],
    () => apiService.getAnomalies(filters),
    {
      refetchInterval: 30000,
    }
  );

  const resolveMutation = useMutation(
    (anomalyId: number) => apiService.resolveAnomaly(anomalyId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('anomalies');
      },
    }
  );

  const handleRefresh = () => {
    queryClient.invalidateQueries('anomalies');
  };

  const handleResolve = (anomalyId: number) => {
    resolveMutation.mutate(anomalyId);
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'low':
        return 'status-warning';
      case 'medium':
        return 'status-warning';
      case 'high':
        return 'status-error';
      case 'critical':
        return 'status-error';
      default:
        return 'status-info';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'low':
      case 'medium':
        return ExclamationTriangleIcon;
      case 'high':
      case 'critical':
        return ExclamationTriangleIcon;
      default:
        return ExclamationTriangleIcon;
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="text-red-800">Failed to load anomalies. Please try again.</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Anomalies</h1>
          <p className="text-gray-600">Detect and investigate unusual patterns</p>
        </div>
        <button
          onClick={handleRefresh}
          className="btn-secondary flex items-center"
        >
          <ArrowPathIcon className="h-4 w-4 mr-2" />
          Refresh
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {['critical', 'high', 'medium', 'low'].map((severity) => {
          const count = anomalies?.filter(a => a.severity === severity).length || 0;
          return (
            <div key={severity} className="card">
              <div className="flex items-center">
                <div className={`p-2 rounded-lg ${
                  severity === 'critical' ? 'bg-red-100' :
                  severity === 'high' ? 'bg-red-50' :
                  severity === 'medium' ? 'bg-yellow-50' :
                  'bg-blue-50'
                }`}>
                  <ExclamationTriangleIcon className={`h-5 w-5 ${
                    severity === 'critical' ? 'text-red-600' :
                    severity === 'high' ? 'text-red-500' :
                    severity === 'medium' ? 'text-yellow-600' :
                    'text-blue-600'
                  }`} />
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-900 capitalize">{severity}</p>
                  <p className="text-2xl font-semibold text-gray-900">{count}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Filters */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Filters</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="label">Start Time</label>
            <input
              type="datetime-local"
              className="input"
              value={filters.start_time}
              onChange={(e) => setFilters({ ...filters, start_time: e.target.value })}
            />
          </div>
          <div>
            <label className="label">End Time</label>
            <input
              type="datetime-local"
              className="input"
              value={filters.end_time}
              onChange={(e) => setFilters({ ...filters, end_time: e.target.value })}
            />
          </div>
          <div>
            <label className="label">Severity</label>
            <select
              className="input"
              value={filters.severity}
              onChange={(e) => setFilters({ ...filters, severity: e.target.value })}
            >
              <option value="">All Severities</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>
        </div>
      </div>

      {/* Anomalies List */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Detected Anomalies</h3>
          <div className="text-sm text-gray-500">
            {anomalies?.length || 0} anomalies found
          </div>
        </div>

        {anomalies && anomalies.length > 0 ? (
          <div className="space-y-4">
            {anomalies.map((anomaly: Anomaly) => {
              const IconComponent = getSeverityIcon(anomaly.severity);
              return (
                <div
                  key={anomaly.id}
                  className={`border rounded-lg p-4 ${
                    anomaly.resolved ? 'bg-gray-50 border-gray-200' : 'bg-white border-gray-300'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0">
                        <IconComponent className="h-5 w-5 text-gray-400" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2">
                          <p className="text-sm font-medium text-gray-900">
                            {anomaly.description}
                          </p>
                          <span className={`status-badge ${getSeverityColor(anomaly.severity)}`}>
                            {anomaly.severity}
                          </span>
                          {anomaly.resolved && (
                            <span className="status-badge status-success">
                              Resolved
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-500 mt-1">
                          Score: {anomaly.score.toFixed(3)} • Metric ID: {anomaly.metric_id}
                        </p>
                        <p className="text-xs text-gray-400 mt-1">
                          Detected: {new Date(anomaly.detected_at).toLocaleString()}
                          {anomaly.resolved_at && ` • Resolved: ${new Date(anomaly.resolved_at).toLocaleString()}`}
                        </p>
                      </div>
                    </div>
                    <div className="flex-shrink-0">
                      {!anomaly.resolved && (
                        <button
                          onClick={() => handleResolve(anomaly.id)}
                          disabled={resolveMutation.isLoading}
                          className="btn-secondary text-xs flex items-center"
                        >
                          <CheckCircleIcon className="h-3 w-3 mr-1" />
                          {resolveMutation.isLoading ? 'Resolving...' : 'Resolve'}
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-12">
            <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No anomalies detected</h3>
            <p className="mt-1 text-sm text-gray-500">
              All systems are operating normally.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
