import React, { useState } from 'react';
import { useQuery } from 'react-query';
import {
  BeakerIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import { CICDPipeline } from '../types';
import { apiService } from '../services/api';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const CICD: React.FC = () => {
  const [filters, setFilters] = useState({
    start_time: '',
    end_time: '',
    status: '',
    limit: 50,
  });

  const { data: pipelines, isLoading, error } = useQuery(
    ['cicd-pipelines', filters],
    () => apiService.getCICDPipelines(filters),
    {
      refetchInterval: 30000,
    }
  );

  const handleRefresh = () => {
    // Query will automatically refetch due to refetchInterval
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'status-success';
      case 'failed':
        return 'status-error';
      case 'running':
        return 'status-info';
      case 'pending':
        return 'status-warning';
      default:
        return 'status-info';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return CheckCircleIcon;
      case 'failed':
        return XCircleIcon;
      case 'running':
        return ClockIcon;
      case 'pending':
        return ClockIcon;
      default:
        return BeakerIcon;
    }
  };

  const formatDuration = (duration?: number) => {
    if (!duration) return '-';
    if (duration < 60) return `${duration.toFixed(1)}s`;
    if (duration < 3600) return `${(duration / 60).toFixed(1)}m`;
    return `${(duration / 3600).toFixed(1)}h`;
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
        <div className="text-red-800">Failed to load CI/CD pipelines. Please try again.</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">CI/CD Pipelines</h1>
          <p className="text-gray-600">Monitor build and deployment pipelines</p>
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
        {['success', 'failed', 'running', 'pending'].map((status) => {
          const count = pipelines?.filter(p => p.status === status).length || 0;
          const IconComponent = getStatusIcon(status);
          return (
            <div key={status} className="card">
              <div className="flex items-center">
                <div className={`p-2 rounded-lg ${
                  status === 'success' ? 'bg-green-100' :
                  status === 'failed' ? 'bg-red-100' :
                  status === 'running' ? 'bg-blue-100' :
                  'bg-yellow-100'
                }`}>
                  <IconComponent className={`h-5 w-5 ${
                    status === 'success' ? 'text-green-600' :
                    status === 'failed' ? 'text-red-600' :
                    status === 'running' ? 'text-blue-600' :
                    'text-yellow-600'
                  }`} />
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-900 capitalize">{status}</p>
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
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
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
            <label className="label">Status</label>
            <select
              className="input"
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
            >
              <option value="">All Statuses</option>
              <option value="success">Success</option>
              <option value="failed">Failed</option>
              <option value="running">Running</option>
              <option value="pending">Pending</option>
            </select>
          </div>
          <div>
            <label className="label">Limit</label>
            <select
              className="input"
              value={filters.limit}
              onChange={(e) => setFilters({ ...filters, limit: parseInt(e.target.value) })}
            >
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
              <option value={200}>200</option>
            </select>
          </div>
        </div>
      </div>

      {/* Pipelines Table */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Recent Pipelines</h3>
          <div className="text-sm text-gray-500">
            {pipelines?.length || 0} pipelines found
          </div>
        </div>

        {pipelines && pipelines.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Pipeline
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Duration
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Branch
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Commit
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Started
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {pipelines.map((pipeline: CICDPipeline) => {
                  const IconComponent = getStatusIcon(pipeline.status);
                  return (
                    <tr key={pipeline.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {pipeline.pipeline_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`status-badge ${getStatusColor(pipeline.status)}`}>
                          <IconComponent className="h-3 w-3 mr-1 inline" />
                          {pipeline.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDuration(pipeline.duration)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {pipeline.branch || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {pipeline.commit_hash ? (
                          <code className="text-xs bg-gray-100 px-1 py-0.5 rounded">
                            {pipeline.commit_hash.substring(0, 8)}
                          </code>
                        ) : '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {pipeline.start_time ? 
                          new Date(pipeline.start_time).toLocaleString() : '-'
                        }
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-12">
            <BeakerIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No pipelines found</h3>
            <p className="mt-1 text-sm text-gray-500">
              No CI/CD pipelines match the current filters.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
