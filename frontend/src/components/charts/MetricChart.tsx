import React from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { Metric } from '../../types';

interface MetricChartProps {
  data: Metric[];
  type?: 'line' | 'area' | 'bar' | 'pie';
  height?: number;
  colors?: string[];
  showGrid?: boolean;
  showLegend?: boolean;
}

const DEFAULT_COLORS = [
  '#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6',
  '#ec4899', '#14b8a6', '#f97316', '#6366f1', '#84cc16'
];

export const MetricChart: React.FC<MetricChartProps> = ({
  data,
  type = 'line',
  height = 300,
  colors = DEFAULT_COLORS,
  showGrid = true,
  showLegend = true
}) => {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg border border-gray-200">
        <p className="text-gray-500">No data available</p>
      </div>
    );
  }

  // Process data for charts
  const chartData = data.map((metric: Metric) => ({
    ...metric,
    timestamp: new Date(metric.timestamp).toLocaleTimeString(),
    value: Number(metric.value)
  }));

  // Group data by metric name for multi-line charts
  const metricNames = Array.from(new Set(data.map((m: Metric) => m.name)));
  const groupedData = metricNames.map((name: string) => ({
    name,
    data: data.filter((m: Metric) => m.name === name).map((m: Metric) => ({
      timestamp: new Date(m.timestamp).toLocaleTimeString(),
      value: Number(m.value)
    }))
  }));

  const renderLineChart = () => (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={chartData}>
        {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />}
        <XAxis 
          dataKey="timestamp" 
          stroke="#6b7280"
          tick={{ fontSize: 12 }}
        />
        <YAxis 
          stroke="#6b7280"
          tick={{ fontSize: 12 }}
        />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: '#ffffff',
            border: '1px solid #e5e7eb',
            borderRadius: '6px'
          }}
        />
        {showLegend && <Legend />}
        {metricNames.map((name: string, index: number) => (
          <Line
            key={name}
            type="monotone"
            dataKey="value"
            stroke={colors[index % colors.length]}
            strokeWidth={2}
            dot={{ r: 3 }}
            activeDot={{ r: 5 }}
            name={name}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );

  const renderAreaChart = () => (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={chartData}>
        {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />}
        <XAxis 
          dataKey="timestamp" 
          stroke="#6b7280"
          tick={{ fontSize: 12 }}
        />
        <YAxis 
          stroke="#6b7280"
          tick={{ fontSize: 12 }}
        />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: '#ffffff',
            border: '1px solid #e5e7eb',
            borderRadius: '6px'
          }}
        />
        {showLegend && <Legend />}
        {metricNames.map((name: string, index: number) => (
          <Area
            key={name}
            type="monotone"
            dataKey="value"
            stroke={colors[index % colors.length]}
            fill={colors[index % colors.length]}
            fillOpacity={0.3}
            strokeWidth={2}
            name={name}
          />
        ))}
      </AreaChart>
    </ResponsiveContainer>
  );

  const renderBarChart = () => (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={chartData}>
        {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />}
        <XAxis 
          dataKey="timestamp" 
          stroke="#6b7280"
          tick={{ fontSize: 12 }}
        />
        <YAxis 
          stroke="#6b7280"
          tick={{ fontSize: 12 }}
        />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: '#ffffff',
            border: '1px solid #e5e7eb',
            borderRadius: '6px'
          }}
        />
        {showLegend && <Legend />}
        {metricNames.map((name: string, index: number) => (
          <Bar
            key={name}
            dataKey="value"
            fill={colors[index % colors.length]}
            name={name}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );

  const renderPieChart = () => {
    // Aggregate data by metric name for pie chart
    const pieData = metricNames.map((name: string, index: number) => ({
      name,
      value: data.filter((m: Metric) => m.name === name).reduce((sum: number, m: Metric) => sum + Number(m.value), 0)
    }));

    return (
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie
            data={pieData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }: { name: string; percent: number }) => `${name} ${(percent * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {pieData.map((entry: any, index: number) => (
              <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
            ))}
          </Pie>
          <Tooltip />
          {showLegend && <Legend />}
        </PieChart>
      </ResponsiveContainer>
    );
  };

  const renderChart = () => {
    switch (type) {
      case 'area':
        return renderAreaChart();
      case 'bar':
        return renderBarChart();
      case 'pie':
        return renderPieChart();
      default:
        return renderLineChart();
    }
  };

  return (
    <div className="w-full">
      {renderChart()}
    </div>
  );
};
