import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  RadialLinearScale,
  ArcElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Doughnut, Radar } from 'react-chartjs-2';
import { SkinPredictionResult } from '@/services/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  RadialLinearScale,
  ArcElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface SkinAnalysisChartProps {
  skinResults: SkinPredictionResult;
}

const SkinAnalysisChart: React.FC<SkinAnalysisChartProps> = ({ skinResults }) => {
  // Create skin type gauge chart
  const gaugeChartData = {
    labels: [''],
    datasets: [
      {
        data: [skinResults.skinType.confidence, 100 - skinResults.skinType.confidence],
        backgroundColor: [
          'rgba(110, 231, 183, 0.8)', // Teal color for confidence
          'rgba(229, 231, 235, 0.3)'  // Gray for remaining
        ],
        borderColor: [
          'rgba(110, 231, 183, 1)',
          'rgba(229, 231, 235, 0.5)'
        ],
        borderWidth: 1,
        cutout: '70%',
        circumference: 180,
        rotation: 270,
      },
    ],
  };

  const gaugeOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        enabled: false,
      },
    },
  };

  // For radar chart of skin issues
  const radarChartData = {
    labels: skinResults.skinIssues.map(issue => issue.name),
    datasets: [
      {
        label: 'Skin Concerns',
        data: skinResults.skinIssues.map(issue => issue.confidence),
        backgroundColor: 'rgba(147, 51, 234, 0.2)',
        borderColor: 'rgba(147, 51, 234, 0.8)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(147, 51, 234, 1)',
        pointHoverRadius: 6,
        pointRadius: 4,
        fill: true,
      },
    ],
  };

  const radarOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      r: {
        angleLines: {
          color: 'rgba(156, 163, 175, 0.2)',
        },
        grid: {
          color: 'rgba(156, 163, 175, 0.2)',
        },
        pointLabels: {
          color: 'rgba(107, 114, 128, 1)',
          font: {
            size: 10,
          },
        },
        ticks: {
          display: false,
          stepSize: 20,
        },
        min: 0,
        max: 100,
      },
    },
    plugins: {
      legend: {
        display: false,
      },
    },
  };

  // Helper function to get color based on skin type
  const getSkinTypeColor = (skinType: string) => {
    const types: Record<string, string> = {
      'dry': 'text-amber-600',
      'oily': 'text-emerald-600',
      'normal': 'text-sky-600',
      'combination': 'text-violet-600',
      'sensitive': 'text-rose-600'
    };
    
    return types[skinType.toLowerCase()] || 'text-primary';
  };
  
  // If no skin issues, display a different message
  const hasSkinIssues = skinResults.skinIssues && skinResults.skinIssues.length > 0;

  return (
    <div className="futuristic-panel p-5 mb-4 w-full">
      <div className="mb-4">
        <h3 className="text-center font-secondary text-base mb-1 gradient-text">Skin Type Analysis</h3>
        <div className="flex flex-col items-center">
          <div className="relative h-28 w-56 mb-2">
            <Doughnut data={gaugeChartData} options={gaugeOptions} />
            <div className="absolute inset-0 flex flex-col items-center justify-center mt-5">
              <span className={`text-2xl font-bold ${getSkinTypeColor(skinResults.skinType.type)}`}>
                {Math.round(skinResults.skinType.confidence)}%
              </span>
              <span className="text-sm font-medium text-gray-600 dark:text-gray-300">
                {skinResults.skinType.type}
              </span>
            </div>
          </div>
        </div>
      </div>
      
      {hasSkinIssues ? (
        <div>
          <h3 className="text-center font-secondary text-base mb-3 gradient-text">Skin Concerns Analysis</h3>
          <div className="h-64 w-full">
            <Radar data={radarChartData} options={radarOptions} />
          </div>
          <div className="mt-4 grid grid-cols-2 gap-2">
            {skinResults.skinIssues.map((issue, index) => (
              <div key={index} className="flex items-center justify-between bg-background/10 backdrop-blur-sm rounded-lg p-2 border border-border/30">
                <span className="text-sm font-medium">{issue.name}</span>
                <span className="text-sm font-semibold bg-primary/10 text-primary px-2 py-1 rounded-full">
                  {Math.round(issue.confidence)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800/30">
          <svg className="w-12 h-12 text-green-500 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-sm font-medium text-green-800 dark:text-green-200">
            Great news! No significant skin issues detected.
          </p>
        </div>
      )}
      
      {skinResults.demographics && (
        <div className="mt-4 p-3 bg-background/10 backdrop-blur-sm rounded-lg border border-border/30">
          <h4 className="text-sm font-medium mb-2 text-center gradient-text">Demographics Analysis</h4>
          <div className="grid grid-cols-3 gap-2 text-center">
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">Age</p>
              <p className="font-medium">{skinResults.demographics.age}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">Gender</p>
              <p className="font-medium">{skinResults.demographics.gender}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">Ethnicity</p>
              <p className="font-medium">{skinResults.demographics.race}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SkinAnalysisChart;
