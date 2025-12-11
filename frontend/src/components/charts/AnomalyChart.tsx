import React from 'react';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
  BarChart,
  Bar,
  PieChart,
  Pie,
  LineChart,
  Line
} from 'recharts';
import { Anomaly } from '../types';

interface AnomalyChartProps {
  data: Anomaly[];
  type?: 'scatter' | 'timeline' | 'severity' | 'distribution';
  height?: number;
  showGrid?: boolean;
}

const SEVERITY_COLORS = {
  low: '#10b981',
  medium: '#f59e0b',
  high: '#ef4444',
  critical: '#991b1b'
};

export const AnomalyChart: React.FC<AnomalyChartProps> = ({
  data,
  type = 'scatter',
  height = 300,
  showGrid = true
}) => {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg border border-gray-200">
        <p className="text-gray-500">No anomaly data available</p>
      </div>
    );
  }

  const renderScatterChart = (): JSX.Element => {
    const chartData = data.map((anomaly: Anomaly, index: number) => ({
      x: new Date(anomaly.detected_at).getTime(),
      y: anomaly.score,
      severity: anomaly.severity,
      id: anomaly.id,
      description: anomaly.description
    }));

    return (
      <ResponsiveContainer width="100%" height={height}>
        <ScatterChart>
          {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />}
          <XAxis 
            type="number" 
            dataKey="x" 
            domain={['dataMin', 'dataMax']}
            tickFormatter={(value: number) => new Date(value).toLocaleDateString()}
            stroke="#6b7280"
          />
          <YAxis 
            dataKey="y" 
            domain={[0, 1]}
            stroke="#6b7280"
            label={{ value: 'Anomaly Score', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip 
            formatter={(value: any, name: string, props: any) => [
              `Score: ${value}`,
              props.payload.description
            ]}
            labelFormatter={(value: any) => `Time: ${new Date(value).toLocaleString()}`}
            contentStyle={{ 
              backgroundColor: '#ffffff',
              border: '1px solid #e5e7eb',
              borderRadius: '6px'
            }}
          />
          <Legend />
          <Scatter name="Anomalies" data={chartData}>
            {chartData.map((entry: any, index: number) => (
              <Cell 
                key={`cell-${index}`} 
                fill={SEVERITY_COLORS[entry.severity as keyof typeof SEVERITY_COLORS]} 
              />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    );
  };

  const renderTimelineChart = () => {
    // Group anomalies by time periods
    const timeGroups = data.reduce((acc: Record<string, any>, anomaly: Anomaly) => {
      const hour = new Date(anomaly.detected_at).getHours();
      const key = `${hour}:00`;
      if (!acc[key]) {
        acc[key] = { time: key, count: 0, critical: 0, high: 0, medium: 0, low: 0 };
      }
      acc[key].count++;
      acc[key][anomaly.severity]++;
      return acc;
    }, {} as Record<string, any>);

    const timelineData = Object.values(timeGroups).sort((a: any, b: any) => 
      a.time.localeCompare(b.time)
    );

    return (
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={timelineData}>
          {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />}
          <XAxis 
            dataKey="time" 
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
          <Bar dataKey="critical" stackId="a" fill={SEVERITY_COLORS.critical} />
          <Bar dataKey="high" stackId="a" fill={SEVERITY_COLORS.high} />
          <Bar dataKey="medium" stackId="a" fill={SEVERITY_COLORS.medium} />
          <Bar dataKey="low" stackId="a" fill={SEVERITY_COLORS.low} />
        </BarChart>
      </ResponsiveContainer>
    );
  };

  const renderSeverityChart = () => {
    const severityData = Object.entries(
      data.reduce((acc: Record<string, number>, anomaly: Anomaly) => {
        acc[anomaly.severity] = (acc[anomaly.severity] || 0) + 1;
        return acc;
      }, {} as Record<string, number>)
    ).map(([severity, count]: [string, number]) => ({
      name: severity.charAt(0).toUpperCase() + severity.slice(1),
      value: count,
      fill: SEVERITY_COLORS[severity as keyof typeof SEVERITY_COLORS]
    }));

    return (
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie
            data={severityData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }: { name: string; percent: number }) => `${name} ${(percent * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {severityData.map((entry: any, index: number) => (
              <Cell key={`cell-${index}`} fill={entry.fill} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    );
  };

  const renderDistributionChart = () => {
    // Create score distribution
    const scoreRanges = [
      { range: '0.0-0.2', min: 0, max: 0.2, count: 0 },
      { range: '0.2-0.4', min: 0.2, max: 0.4, count: 0 },
      { range: '0.4-0.6', min: 0.4, max: 0.6, count: 0 },
      { range: '0.6-0.8', min: 0.6, max: 0.8, count: 0 },
      { range: '0.8-1.0', min: 0.8, max: 1.0, count: 0 }
    ];

    data.forEach((anomaly: Anomaly) => {
      const range = scoreRanges.find((r: any) => 
        anomaly.score >= r.min && anomaly.score < r.max
      );
      if (range) range.count++;
    });

    return (
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={scoreRanges}>
          {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />}
          <XAxis 
            dataKey="range" 
            stroke="#6b7280"
            tick={{ fontSize: 12 }}
          />
          <YAxis 
            stroke="#6b7280"
            tick={{ fontSize: 12 }}
            label={{ value: 'Count', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#ffffff',
              border: '1px solid #e5e7eb',
              borderRadius: '6px'
            }}
          />
          <Bar 
            dataKey="count" 
            fill="#3b82f6"
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    );
  };

  const renderChart = () => {
    switch (type) {
      case 'timeline':
        return renderTimelineChart();
      case 'severity':
        return renderSeverityChart();
      case 'distribution':
        return renderDistributionChart();
      default:
        return renderScatterChart();
    }
  };

  return (
    <div className="w-full">
      {renderChart()}
    </div>
  );
};
