import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { ChartBarIcon, PlusIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import { Metric } from '../types';
import { apiService } from '../services/api';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const Metrics: React.FC = () => {
  const [filters, setFilters] = useState({
    start_time: '',
    end_time: '',
    metric_type: '',
  });

  const queryClient = useQueryClient();

  const { data: metrics, isLoading, error } = useQuery(
    ['metrics', filters],
    () => apiService.getMetrics(filters),
    {
      refetchInterval: 30000,
    }
  );

  const ingestMutation = useMutation(
    (metricData: any) => apiService.ingestMetrics(metricData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('metrics');
      },
    }
  );

  const handleRefresh = () => {
    queryClient.invalidateQueries('metrics');
  };

  const handleIngestSample = () => {
    const sampleData = {
      name: 'sample_metric',
      value: Math.random() * 100,
      unit: 'percent',
      source: 'demo',
      tags: { environment: 'demo' },
    };
    ingestMutation.mutate(sampleData);
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
        <div className="text-red-800">Failed to load metrics. Please try again.</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Metrics</h1>
          <p className="text-gray-600">Monitor and analyze system metrics</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={handleIngestSample}
            disabled={ingestMutation.isLoading}
            className="btn-primary flex items-center"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            {ingestMutation.isLoading ? 'Adding...' : 'Add Sample'}
          </button>
          <button
            onClick={handleRefresh}
            className="btn-secondary flex items-center"
          >
            <ArrowPathIcon className="h-4 w-4 mr-2" />
            Refresh
          </button>
        </div>
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
            <label className="label">Metric Type</label>
            <input
              type="text"
              className="input"
              placeholder="Filter by metric name"
              value={filters.metric_type}
              onChange={(e) => setFilters({ ...filters, metric_type: e.target.value })}
            />
          </div>
        </div>
      </div>

      {/* Metrics Table */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Recent Metrics</h3>
          <div className="text-sm text-gray-500">
            {metrics?.length || 0} metrics found
          </div>
        </div>

        {metrics && metrics.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Value
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Unit
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Source
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Timestamp
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {metrics.map((metric: Metric) => (
                  <tr key={metric.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {metric.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {metric.value.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {metric.unit || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {metric.source}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(metric.timestamp).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-12">
            <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No metrics</h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by adding some sample metrics.
            </p>
            <div className="mt-6">
              <button
                onClick={handleIngestSample}
                disabled={ingestMutation.isLoading}
                className="btn-primary"
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Add Sample Metric
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Chart Placeholder */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Metrics Visualization</h3>
        <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <div className="text-center">
            <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
            <p className="mt-2 text-sm text-gray-500">Interactive charts will be displayed here</p>
          </div>
        </div>
      </div>
    </div>
  );
};
