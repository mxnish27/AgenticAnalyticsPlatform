import React, { useState } from 'react';
import { useQuery } from 'react-query';
import {
  DocumentTextIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  RefreshIcon
} from '@heroicons/react/24/outline';
import { LogEntry } from '../types';
import { apiService } from '../services/api';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const Logs: React.FC = () => {
  const [filters, setFilters] = useState({
    start_time: '',
    end_time: '',
    level: '',
    source: '',
    limit: 100,
  });

  const { data: logs, isLoading, error } = useQuery(
    ['logs', filters],
    () => apiService.getLogEntries(filters),
    {
      refetchInterval: 30000,
    }
  );

  const handleRefresh = () => {
    // Query will automatically refetch due to refetchInterval
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'FATAL':
      case 'ERROR':
        return 'status-error';
      case 'WARN':
        return 'status-warning';
      case 'INFO':
        return 'status-info';
      case 'DEBUG':
        return 'status-success';
      default:
        return 'status-info';
    }
  };

  const getLevelIcon = (level: string) => {
    switch (level) {
      case 'FATAL':
      case 'ERROR':
        return ExclamationTriangleIcon;
      case 'WARN':
        return ExclamationTriangleIcon;
      case 'INFO':
        return CheckCircleIcon;
      case 'DEBUG':
        return DocumentTextIcon;
      default:
        return DocumentTextIcon;
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
        <div className="text-red-800">Failed to load logs. Please try again.</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Logs</h1>
          <p className="text-gray-600">Browse and search system logs</p>
        </div>
        <button
          onClick={handleRefresh}
          className="btn-secondary flex items-center"
        >
          <RefreshIcon className="h-4 w-4 mr-2" />
          Refresh
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        {['ERROR', 'WARN', 'INFO', 'DEBUG', 'FATAL'].map((level) => {
          const count = logs?.filter(l => l.level === level).length || 0;
          const IconComponent = getLevelIcon(level);
          return (
            <div key={level} className="card">
              <div className="flex items-center">
                <div className={`p-2 rounded-lg ${
                  level === 'ERROR' || level === 'FATAL' ? 'bg-red-100' :
                  level === 'WARN' ? 'bg-yellow-100' :
                  level === 'INFO' ? 'bg-blue-100' :
                  'bg-green-100'
                }`}>
                  <IconComponent className={`h-5 w-5 ${
                    level === 'ERROR' || level === 'FATAL' ? 'text-red-600' :
                    level === 'WARN' ? 'text-yellow-600' :
                    level === 'INFO' ? 'text-blue-600' :
                    'text-green-600'
                  }`} />
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-900">{level}</p>
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
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
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
            <label className="label">Level</label>
            <select
              className="input"
              value={filters.level}
              onChange={(e) => setFilters({ ...filters, level: e.target.value })}
            >
              <option value="">All Levels</option>
              <option value="DEBUG">Debug</option>
              <option value="INFO">Info</option>
              <option value="WARN">Warning</option>
              <option value="ERROR">Error</option>
              <option value="FATAL">Fatal</option>
            </select>
          </div>
          <div>
            <label className="label">Source</label>
            <input
              type="text"
              className="input"
              placeholder="Filter by source"
              value={filters.source}
              onChange={(e) => setFilters({ ...filters, source: e.target.value })}
            />
          </div>
          <div>
            <label className="label">Limit</label>
            <select
              className="input"
              value={filters.limit}
              onChange={(e) => setFilters({ ...filters, limit: parseInt(e.target.value) })}
            >
              <option value={50}>50</option>
              <option value={100}>100</option>
              <option value={200}>200</option>
              <option value={500}>500</option>
            </select>
          </div>
        </div>
      </div>

      {/* Logs List */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Log Entries</h3>
          <div className="text-sm text-gray-500">
            {logs?.length || 0} entries found
          </div>
        </div>

        {logs && logs.length > 0 ? (
          <div className="space-y-2">
            {logs.map((log: LogEntry) => {
              const IconComponent = getLevelIcon(log.level);
              return (
                <div
                  key={log.id}
                  className="border rounded-lg p-3 bg-white hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 mt-0.5">
                      <IconComponent className="h-4 w-4 text-gray-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        <span className={`status-badge ${getLevelColor(log.level)}`}>
                          {log.level}
                        </span>
                        <span className="text-xs text-gray-500">
                          {log.source}
                        </span>
                        <span className="text-xs text-gray-400">
                          {new Date(log.timestamp).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-sm text-gray-900 mt-1 font-mono">
                        {log.message}
                      </p>
                      {log.metadata && Object.keys(log.metadata).length > 0 && (
                        <details className="mt-2">
                          <summary className="text-xs text-gray-500 cursor-pointer">
                            Metadata
                          </summary>
                          <pre className="text-xs text-gray-600 mt-1 bg-gray-50 p-2 rounded">
                            {JSON.stringify(log.metadata, null, 2)}
                          </pre>
                        </details>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-12">
            <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No logs found</h3>
            <p className="mt-1 text-sm text-gray-500">
              No log entries match the current filters.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
