import React, { useState } from 'react';
import { ChatInterface } from '../components/ChatInterface';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { 
  ChartBarIcon, 
  DocumentTextIcon, 
  LightBulbIcon,
  ArrowDownTrayIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

interface Insight {
  id: string;
  content: string;
  type: 'anomaly' | 'trend' | 'recommendation';
  timestamp: Date;
  confidence: number;
}

export const AnalyticsChat: React.FC = () => {
  const [insights, setInsights] = useState<Insight[]>([]);
  const [isExporting, setIsExporting] = useState(false);

  const handleInsightGenerated = (newInsights: any[]): void => {
    const formattedInsights: Insight[] = newInsights.map((insight: any, index: number) => ({
      id: `insight-${Date.now()}-${index}`,
      content: insight.content || insight.summary || 'New insight generated',
      type: insight.type || 'recommendation',
      timestamp: new Date(),
      confidence: insight.confidence || 0.8
    }));

    setInsights((prev: Insight[]) => [...prev, ...formattedInsights].slice(0, 10)); // Keep last 10 insights
  };

  const handleExport = async (): Promise<void> => {
    setIsExporting(true);
    try {
      const exportData = {
        insights: insights.map((insight: Insight) => ({
          ...insight,
          timestamp: insight.timestamp.toISOString()
        })),
        exportedAt: new Date().toISOString()
      };

      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json'
      });

      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analytics-insights-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setIsExporting(false);
    }
  };

  const clearInsights = (): void => {
    setInsights([]);
  };

  const getInsightIcon = (type: string): JSX.Element => {
    switch (type) {
      case 'anomaly':
        return <ExclamationTriangleIcon className="h-4 w-4 text-red-500" />;
      case 'trend':
        return <ChartBarIcon className="h-4 w-4 text-blue-500" />;
      default:
        return <LightBulbIcon className="h-4 w-4 text-green-500" />;
    }
  };

  return (
    <div className="h-full flex">
      {/* Chat Interface */}
      <div className="flex-1 flex flex-col">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Analytics Chat</h1>
            <p className="text-gray-600">Ask questions about your data and get AI-powered insights</p>
          </div>
        </div>

        <div className="flex-1 p-6">
          <ChatInterface 
            onInsightGenerated={handleInsightGenerated}
            className="h-full"
          />
        </div>
      </div>

      {/* Insights Sidebar */}
      <div className="w-80 border-l border-gray-200 bg-gray-50 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900 flex items-center">
              <LightBulbIcon className="h-5 w-5 text-yellow-500 mr-2" />
              Recent Insights
            </h3>
            <div className="flex space-x-2">
              {insights.length > 0 && (
                <>
                  <button
                    onClick={handleExport}
                    disabled={isExporting}
                    className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-50"
                    title="Export insights"
                  >
                    {isExporting ? (
                      <LoadingSpinner size="small" />
                    ) : (
                      <ArrowDownTrayIcon className="h-4 w-4" />
                    )}
                  </button>
                  <button
                    onClick={clearInsights}
                    className="p-1 text-gray-400 hover:text-gray-600"
                    title="Clear insights"
                  >
                    ×
                  </button>
                </>
              )}
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            {insights.length} insights generated
          </p>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {insights.length === 0 ? (
            <div className="text-center py-8">
              <LightBulbIcon className="h-12 w-12 text-gray-300 mx-auto mb-3" />
              <p className="text-sm text-gray-500">
                Start chatting with the AI assistant to generate insights
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {insights.map((insight: Insight) => (
                <div
                  key={insight.id}
                  className="bg-white p-3 rounded-lg border border-gray-200 hover:shadow-sm transition-shadow"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center mb-1">
                        {getInsightIcon(insight.type)}
                        <span className="ml-2 text-sm font-medium text-gray-900">
                          {insight.type.charAt(0).toUpperCase() + insight.type.slice(1)}
                        </span>
                      </div>
                      <p className="text-xs text-gray-600 mb-2">
                        {insight.content}
                      </p>
                      <div className="flex items-center space-x-2">
                        <span className="text-xs text-gray-400">
                          Confidence: {Math.round(insight.confidence * 100)}%
                        </span>
                        <span className="text-xs text-gray-400">
                          {insight.timestamp.toLocaleTimeString()}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="p-4 border-t border-gray-200">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Quick Actions</h4>
          <div className="space-y-2">
            <button className="w-full flex items-center px-3 py-2 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors">
              <ChartBarIcon className="h-4 w-4 text-gray-400 mr-2" />
              View Analytics Dashboard
            </button>
            <button className="w-full flex items-center px-3 py-2 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors">
              <DocumentTextIcon className="h-4 w-4 text-gray-400 mr-2" />
              Generate Report
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
