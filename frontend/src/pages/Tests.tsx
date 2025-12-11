import React, { useState } from 'react';
import { useQuery } from 'react-query';
import {
  DocumentDuplicateIcon,
  CheckCircleIcon,
  XCircleIcon,
  ForwardIcon,
  RefreshIcon
} from '@heroicons/react/24/outline';
import { TestResult } from '../types';
import { apiService } from '../services/api';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const Tests: React.FC = () => {
  const [filters, setFilters] = useState({
    start_time: '',
    end_time: '',
    status: '',
    test_suite: '',
    limit: 50,
  });

  const { data: tests, isLoading, error } = useQuery(
    ['test-results', filters],
    () => apiService.getTestResults(filters),
    {
      refetchInterval: 30000,
    }
  );

  const handleRefresh = () => {
    // Query will automatically refetch due to refetchInterval
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'passed':
        return 'status-success';
      case 'failed':
        return 'status-error';
      case 'skipped':
        return 'status-warning';
      default:
        return 'status-info';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'passed':
        return CheckCircleIcon;
      case 'failed':
        return XCircleIcon;
      case 'skipped':
        return ForwardIcon;
      default:
        return DocumentDuplicateIcon;
    }
  };

  const formatDuration = (duration?: number) => {
    if (!duration) return '-';
    if (duration < 1000) return `${duration.toFixed(0)}ms`;
    return `${(duration / 1000).toFixed(2)}s`;
  };

  const calculatePassRate = (testResults: TestResult[]) => {
    if (!testResults || testResults.length === 0) return 0;
    const passed = testResults.filter(t => t.status === 'passed').length;
    return (passed / testResults.length * 100).toFixed(1);
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
        <div className="text-red-800">Failed to load test results. Please try again.</div>
      </div>
    );
  }

  const passRate = calculatePassRate(tests || []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Test Results</h1>
          <p className="text-gray-600">View and analyze test execution results</p>
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
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-blue-500">
              <DocumentDuplicateIcon className="h-6 w-6 text-white" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">Total Tests</dt>
                <dd className="text-2xl font-semibold text-gray-900">
                  {tests?.length || 0}
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-green-500">
              <CheckCircleIcon className="h-6 w-6 text-white" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">Passed</dt>
                <dd className="text-2xl font-semibold text-gray-900">
                  {tests?.filter(t => t.status === 'passed').length || 0}
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-red-500">
              <XCircleIcon className="h-6 w-6 text-white" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">Failed</dt>
                <dd className="text-2xl font-semibold text-gray-900">
                  {tests?.filter(t => t.status === 'failed').length || 0}
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-purple-500">
              <DocumentDuplicateIcon className="h-6 w-6 text-white" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">Pass Rate</dt>
                <dd className="text-2xl font-semibold text-gray-900">{passRate}%</dd>
              </dl>
            </div>
          </div>
        </div>
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
            <label className="label">Status</label>
            <select
              className="input"
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
            >
              <option value="">All Statuses</option>
              <option value="passed">Passed</option>
              <option value="failed">Failed</option>
              <option value="skipped">Skipped</option>
            </select>
          </div>
          <div>
            <label className="label">Test Suite</label>
            <input
              type="text"
              className="input"
              placeholder="Filter by suite"
              value={filters.test_suite}
              onChange={(e) => setFilters({ ...filters, test_suite: e.target.value })}
            />
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

      {/* Test Results Table */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Test Results</h3>
          <div className="text-sm text-gray-500">
            {tests?.length || 0} tests found
          </div>
        </div>

        {tests && tests.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Test Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Suite
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Duration
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Error Message
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Timestamp
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {tests.map((test: TestResult) => {
                  const IconComponent = getStatusIcon(test.status);
                  return (
                    <tr key={test.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {test.test_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {test.test_suite}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`status-badge ${getStatusColor(test.status)}`}>
                          <IconComponent className="h-3 w-3 mr-1 inline" />
                          {test.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDuration(test.duration)}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                        {test.error_message || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(test.timestamp).toLocaleString()}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-12">
            <DocumentDuplicateIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No test results found</h3>
            <p className="mt-1 text-sm text-gray-500">
              No test results match the current filters.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
