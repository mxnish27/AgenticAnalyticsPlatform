import React from 'react';
import {
  RadialBarChart,
  RadialBar,
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';

interface SystemHealthChartProps {
  data: {
    cpu: number;
    memory: number;
    disk: number;
    network: number;
    errorRate: number;
    responseTime: number;
  };
  type?: 'radial' | 'gauge' | 'comparison';
  height?: number;
}

interface HealthIndicatorProps {
  value: number;
  label: string;
  threshold?: { warning: number; critical: number };
  unit?: string;
  size?: 'small' | 'medium' | 'large';
}

const HEALTH_COLORS = {
  excellent: '#10b981',
  good: '#3b82f6',
  warning: '#f59e0b',
  critical: '#ef4444'
};

const getHealthColor = (value: number, thresholds = { warning: 70, critical: 90 }): string => {
  if (value < thresholds.warning) return HEALTH_COLORS.excellent;
  if (value < thresholds.critical) return HEALTH_COLORS.warning;
  return HEALTH_COLORS.critical;
};

export const SystemHealthChart: React.FC<SystemHealthChartProps> = ({
  data,
  type = 'radial',
  height = 300
}) => {
  const radialData = [
    { name: 'CPU', value: data.cpu, fill: getHealthColor(data.cpu) },
    { name: 'Memory', value: data.memory, fill: getHealthColor(data.memory) },
    { name: 'Disk', value: data.disk, fill: getHealthColor(data.disk) },
    { name: 'Network', value: data.network, fill: getHealthColor(data.network) }
  ];

  const gaugeData = [
    { name: 'System Health', value: (100 - data.errorRate), fill: getHealthColor(100 - data.errorRate) }
  ];

  const comparisonData = [
    { metric: 'CPU', current: data.cpu, threshold: 80, color: getHealthColor(data.cpu) },
    { metric: 'Memory', current: data.memory, threshold: 85, color: getHealthColor(data.memory) },
    { metric: 'Disk', current: data.disk, threshold: 90, color: getHealthColor(data.disk) },
    { metric: 'Error Rate', current: data.errorRate, threshold: 10, color: getHealthColor(data.errorRate) },
    { metric: 'Response Time', current: data.responseTime, threshold: 500, color: getHealthColor(data.responseTime / 5) }
  ];

  const renderRadialChart = () => (
    <ResponsiveContainer width="100%" height={height}>
      <RadialBarChart cx="50%" cy="50%" innerRadius="10%" outerRadius="90%" data={radialData}>
        <RadialBar
          dataKey="value"
          cornerRadius={10}
          fill="#8884d8"
          label={{ position: 'insideStart', fill: '#fff' }}
        />
        <Legend />
        <Tooltip 
          formatter={(value: any) => [`${value}%`, 'Usage']}
          contentStyle={{ 
            backgroundColor: '#ffffff',
            border: '1px solid #e5e7eb',
            borderRadius: '6px'
          }}
        />
      </RadialBarChart>
    </ResponsiveContainer>
  );

  const renderGaugeChart = () => (
    <ResponsiveContainer width="100%" height={height}>
      <RadialBarChart cx="50%" cy="50%" innerRadius="60%" outerRadius="90%" data={gaugeData}>
        <RadialBar
          dataKey="value"
          cornerRadius={10}
          fill={gaugeData[0].fill}
          max={100}
        />
        <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle" className="text-2xl font-bold">
          {gaugeData[0].value.toFixed(1)}%
        </text>
        <text x="50%" y="60%" textAnchor="middle" dominantBaseline="middle" className="text-sm text-gray-500">
          System Health
        </text>
        <Tooltip 
          formatter={(value: any) => [`${value}%`, 'Health Score']}
          contentStyle={{ 
            backgroundColor: '#ffffff',
            border: '1px solid #e5e7eb',
            borderRadius: '6px'
          }}
        />
      </RadialBarChart>
    </ResponsiveContainer>
  );

  const renderComparisonChart = () => (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={comparisonData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis 
          dataKey="metric" 
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
        <Legend />
        <Bar 
          dataKey="current" 
          fill="#3b82f6" 
          name="Current"
          radius={[4, 4, 0, 0]}
        />
        <Bar 
          dataKey="threshold" 
          fill="#ef4444" 
          name="Threshold"
          radius={[4, 4, 0, 0]}
          opacity={0.6}
        />
      </BarChart>
    </ResponsiveContainer>
  );

  const renderChart = () => {
    switch (type) {
      case 'gauge':
        return renderGaugeChart();
      case 'comparison':
        return renderComparisonChart();
      default:
        return renderRadialChart();
    }
  };

  return (
    <div className="w-full">
      {renderChart()}
    </div>
  );
};

interface HealthIndicatorProps {
  value: number;
  label: string;
  threshold?: { warning: number; critical: number };
  unit?: string;
  size?: 'small' | 'medium' | 'large';
}

export const HealthIndicator: React.FC<HealthIndicatorProps> = ({
  value,
  label,
  threshold = { warning: 70, critical: 90 },
  unit = '%',
  size = 'medium'
}) => {
  const color = getHealthColor(value, threshold);
  
  const sizeClasses: Record<string, string> = {
    small: 'w-16 h-16',
    medium: 'w-24 h-24',
    large: 'w-32 h-32'
  };

  const textSizes: Record<string, string> = {
    small: 'text-sm',
    medium: 'text-base',
    large: 'text-lg'
  };

  return (
    <div className="flex flex-col items-center space-y-2">
      <div className={`${sizeClasses[size]} relative`}>
        <svg className="transform -rotate-90 w-full h-full">
          <circle
            cx="50%"
            cy="50%"
            r="40%"
            stroke="#e5e7eb"
            strokeWidth="8"
            fill="none"
          />
          <circle
            cx="50%"
            cy="50%"
            r="40%"
            stroke={color}
            strokeWidth="8"
            fill="none"
            strokeDasharray={`${2 * Math.PI * 40}`}
            strokeDashoffset={`${2 * Math.PI * 40 * (1 - value / 100)}`}
            className="transition-all duration-500 ease-out"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={`${textSizes[size]} font-bold`}>
            {value.toFixed(0)}{unit}
          </span>
        </div>
      </div>
      <span className="text-sm text-gray-600">{label}</span>
    </div>
  );
};
