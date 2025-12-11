import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { CogIcon, PlusIcon, TrashIcon, PencilIcon } from '@heroicons/react/24/outline';
import { DataSource } from '../types';
import { apiService } from '../services/api';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const Settings: React.FC = () => {
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingSource, setEditingSource] = useState<DataSource | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    type: 'logs' as 'logs' | 'metrics' | 'cicd' | 'tests',
    config: '{}',
    enabled: true,
  });

  const queryClient = useQueryClient();

  const { data: dataSources, isLoading, error } = useQuery(
    'data-sources',
    () => apiService.getDataSources(),
    {
      refetchInterval: 30000,
    }
  );

  const createMutation = useMutation(
    (dataSource: Partial<DataSource>) => apiService.createDataSource(dataSource),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('data-sources');
        setShowAddForm(false);
        resetForm();
      },
    }
  );

  const updateMutation = useMutation(
    ({ id, dataSource }: { id: number; dataSource: Partial<DataSource> }) =>
      apiService.updateDataSource(id, dataSource),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('data-sources');
        setEditingSource(null);
        resetForm();
      },
    }
  );

  const deleteMutation = useMutation(
    (id: number) => apiService.deleteDataSource(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('data-sources');
      },
    }
  );

  const resetForm = () => {
    setFormData({
      name: '',
      type: 'logs',
      config: '{}',
      enabled: true,
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const config = JSON.parse(formData.config);
      if (editingSource) {
        updateMutation.mutate({ id: editingSource.id, dataSource: { ...formData, config } });
      } else {
        createMutation.mutate({ ...formData, config });
      }
    } catch (error) {
      alert('Invalid JSON in config field');
    }
  };

  const handleEdit = (source: DataSource) => {
    setEditingSource(source);
    setFormData({
      name: source.name,
      type: source.type,
      config: JSON.stringify(source.config, null, 2),
      enabled: source.enabled,
    });
    setShowAddForm(true);
  };

  const handleDelete = (id: number) => {
    if (confirm('Are you sure you want to delete this data source?')) {
      deleteMutation.mutate(id);
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'logs':
        return 'status-info';
      case 'metrics':
        return 'status-success';
      case 'cicd':
        return 'status-warning';
      case 'tests':
        return 'status-error';
      default:
        return 'status-info';
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
        <div className="text-red-800">Failed to load data sources. Please try again.</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600">Manage data sources and configuration</p>
        </div>
        <button
          onClick={() => {
            setEditingSource(null);
            resetForm();
            setShowAddForm(true);
          }}
          className="btn-primary flex items-center"
        >
          <PlusIcon className="h-4 w-4 mr-2" />
          Add Data Source
        </button>
      </div>

      {/* Add/Edit Form */}
      {showAddForm && (
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            {editingSource ? 'Edit Data Source' : 'Add New Data Source'}
          </h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Name</label>
                <input
                  type="text"
                  className="input"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>
              <div>
                <label className="label">Type</label>
                <select
                  className="input"
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value as any })}
                >
                  <option value="logs">Logs</option>
                  <option value="metrics">Metrics</option>
                  <option value="cicd">CI/CD</option>
                  <option value="tests">Tests</option>
                </select>
              </div>
            </div>
            <div>
              <label className="label">Configuration (JSON)</label>
              <textarea
                className="input"
                rows={6}
                value={formData.config}
                onChange={(e) => setFormData({ ...formData, config: e.target.value })}
                placeholder='{"key": "value"}'
                required
              />
            </div>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="enabled"
                checked={formData.enabled}
                onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="enabled" className="ml-2 block text-sm text-gray-900">
                Enabled
              </label>
            </div>
            <div className="flex space-x-3">
              <button
                type="submit"
                disabled={createMutation.isLoading || updateMutation.isLoading}
                className="btn-primary"
              >
                {createMutation.isLoading || updateMutation.isLoading ? (
                  <>
                    <LoadingSpinner size="small" className="mr-2" />
                    Saving...
                  </>
                ) : editingSource ? (
                  'Update'
                ) : (
                  'Create'
                )}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowAddForm(false);
                  setEditingSource(null);
                  resetForm();
                }}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Data Sources List */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Data Sources</h3>
          <div className="text-sm text-gray-500">
            {dataSources?.length || 0} sources configured
          </div>
        </div>

        {dataSources && dataSources.length > 0 ? (
          <div className="space-y-4">
            {dataSources.map((source: DataSource) => (
              <div
                key={source.id}
                className={`border rounded-lg p-4 ${
                  source.enabled ? 'bg-white border-gray-300' : 'bg-gray-50 border-gray-200'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0">
                      <CogIcon className="h-5 w-5 text-gray-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        <p className="text-sm font-medium text-gray-900">
                          {source.name}
                        </p>
                        <span className={`status-badge ${getTypeColor(source.type)}`}>
                          {source.type}
                        </span>
                        {!source.enabled && (
                          <span className="status-badge status-warning">
                            Disabled
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-gray-500 mt-1">
                        Created: {new Date(source.created_at).toLocaleString()}
                        {source.last_sync && ` • Last sync: ${new Date(source.last_sync).toLocaleString()}`}
                      </p>
                      <details className="mt-2">
                        <summary className="text-xs text-gray-500 cursor-pointer">
                          Configuration
                        </summary>
                        <pre className="text-xs text-gray-600 mt-1 bg-gray-50 p-2 rounded overflow-x-auto">
                          {JSON.stringify(source.config, null, 2)}
                        </pre>
                      </details>
                    </div>
                  </div>
                  <div className="flex-shrink-0 flex space-x-2">
                    <button
                      onClick={() => handleEdit(source)}
                      className="btn-secondary text-xs flex items-center"
                    >
                      <PencilIcon className="h-3 w-3 mr-1" />
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(source.id)}
                      disabled={deleteMutation.isLoading}
                      className="btn-error text-xs flex items-center"
                    >
                      <TrashIcon className="h-3 w-3 mr-1" />
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <CogIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No data sources configured</h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by adding your first data source.
            </p>
            <div className="mt-6">
              <button
                onClick={() => {
                  setEditingSource(null);
                  resetForm();
                  setShowAddForm(true);
                }}
                className="btn-primary"
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Add Data Source
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
