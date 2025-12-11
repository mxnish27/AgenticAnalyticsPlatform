import React from 'react';
import { useQuery } from 'react-query';
import {
  ChartBarIcon,
  ExclamationTriangleIcon,
  ServerIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import { AnalyticsSummary } from '../types';
import { apiService } from '../services/api';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const Dashboard: React.FC = () => {
  const { data: summary, isLoading, error } = useQuery(
    'analytics-summary',
    () => apiService.getAnalyticsSummary('24h'),
    {
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  );

  const stats = [
    {
      name: 'Total Metrics',
      value: summary?.total_metrics || 0,
      icon: ChartBarIcon,
      color: 'bg-blue-500',
      change: '+12%',
      changeType: 'positive',
    },
    {
      name: 'Anomalies Detected',
      value: summary?.total_anomalies || 0,
      icon: ExclamationTriangleIcon,
      color: 'bg-red-500',
      change: '+3%',
      changeType: 'negative',
    },
    {
      name: 'Active Data Sources',
      value: summary?.active_data_sources || 0,
      icon: ServerIcon,
      color: 'bg-green-500',
      change: '0%',
      changeType: 'neutral',
    },
    {
      name: 'Test Pass Rate',
      value: `${summary?.test_pass_rate.toFixed(1) || 0}%`,
      icon: CheckCircleIcon,
      color: 'bg-purple-500',
      change: '+5%',
      changeType: 'positive',
    },
  ];

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
        <div className="text-red-800">Failed to load dashboard data. Please try again.</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Welcome to your Agentic Analytics Platform</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.name} className="metric-card">
            <div className="flex items-center">
              <div className={`p-3 rounded-lg ${stat.color}`}>
                <stat.icon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">{stat.name}</dt>
                  <dd className="flex items-baseline">
                    <div className="text-2xl font-semibold text-gray-900">{stat.value}</div>
                    <div
                      className={`ml-2 flex items-baseline text-sm font-semibold ${
                        stat.changeType === 'positive'
                          ? 'text-green-600'
                          : stat.changeType === 'negative'
                          ? 'text-red-600'
                          : 'text-gray-500'
                      }`}
                    >
                      {stat.change}
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Metrics Chart Placeholder */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Metrics</h3>
          <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
            <div className="text-center">
              <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-2 text-sm text-gray-500">Metrics chart will be displayed here</p>
            </div>
          </div>
        </div>

        {/* Anomalies Chart Placeholder */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Anomaly Trends</h3>
          <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
            <div className="text-center">
              <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-2 text-sm text-gray-500">Anomaly trends will be displayed here</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
        <div className="flow-root">
          <ul className="-mb-8">
            {[1, 2, 3].map((item) => (
              <li key={item}>
                <div className="relative pb-8">
                  {item !== 3 && (
                    <span
                      className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                      aria-hidden="true"
                    />
                  )}
                  <div className="relative flex space-x-3">
                    <div>
                      <span className="h-8 w-8 rounded-full bg-primary-500 flex items-center justify-center ring-8 ring-white">
                        <ChartBarIcon className="h-4 w-4 text-white" />
                      </span>
                    </div>
                    <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                      <div>
                        <p className="text-sm text-gray-500">
                          New metrics ingested from <span className="font-medium text-gray-900">production</span>
                        </p>
                      </div>
                      <div className="text-right text-sm whitespace-nowrap text-gray-500">
                        {item}h ago
                      </div>
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <button className="btn-primary text-left">
            <ChartBarIcon className="h-5 w-5 mb-2" />
            <div className="font-medium">View Metrics</div>
            <div className="text-sm opacity-90">Explore all metrics</div>
          </button>
          <button className="btn-secondary text-left">
            <ExclamationTriangleIcon className="h-5 w-5 mb-2" />
            <div className="font-medium">Check Anomalies</div>
            <div className="text-sm opacity-90">Review detected issues</div>
          </button>
          <button className="btn-secondary text-left">
            <ServerIcon className="h-5 w-5 mb-2" />
            <div className="font-medium">Data Sources</div>
            <div className="text-sm opacity-90">Manage connections</div>
          </button>
          <button className="btn-secondary text-left">
            <CheckCircleIcon className="h-5 w-5 mb-2" />
            <div className="font-medium">Test Results</div>
            <div className="text-sm opacity-90">View test reports</div>
          </button>
        </div>
      </div>
    </div>
  );
};
