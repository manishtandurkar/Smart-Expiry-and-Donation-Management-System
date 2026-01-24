import React, { useEffect, useState } from 'react';
import { statsAPI } from '../services/api';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Bar, Pie, Doughnut } from 'react-chartjs-2';
import './Charts.css';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

export default function Charts() {
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchChartData();
  }, []);

  const fetchChartData = async () => {
    try {
      setLoading(true);
      const response = await statsAPI.getChartData();
      setChartData(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch chart data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="charts-container">
        <div className="loading">Loading charts...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="charts-container">
        <div className="error-message">{error}</div>
      </div>
    );
  }

  if (!chartData) return null;

  // Color palettes
  const categoryColors = [
    'rgba(59, 130, 246, 0.8)',   // Blue
    'rgba(16, 185, 129, 0.8)',   // Green
    'rgba(251, 146, 60, 0.8)',   // Orange
    'rgba(139, 92, 246, 0.8)',   // Purple
    'rgba(236, 72, 153, 0.8)',   // Pink
    'rgba(34, 197, 94, 0.8)',    // Light Green
    'rgba(245, 158, 11, 0.8)',   // Amber
    'rgba(99, 102, 241, 0.8)',   // Indigo
  ];

  const expiryColors = {
    'Expired': 'rgba(239, 68, 68, 0.8)',      // Red
    'Critical': 'rgba(249, 115, 22, 0.8)',    // Orange
    'Warning': 'rgba(234, 179, 8, 0.8)',      // Yellow
    'Safe': 'rgba(34, 197, 94, 0.8)',         // Green
  };

  // 1. Category Distribution (Pie Chart)
  const categoryChartData = {
    labels: chartData.category_distribution.map(c => c.category),
    datasets: [{
      label: 'Items',
      data: chartData.category_distribution.map(c => c.count),
      backgroundColor: categoryColors,
      borderColor: 'rgba(255, 255, 255, 1)',
      borderWidth: 2,
    }],
  };

  const categoryOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right',
        labels: {
          padding: 15,
          font: {
            size: 12,
          },
        },
      },
      title: {
        display: true,
        text: 'Items by Category',
        font: {
          size: 18,
          weight: 'bold',
        },
        padding: {
          top: 10,
          bottom: 20,
        },
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const label = context.label || '';
            const value = context.parsed || 0;
            const total = context.dataset.data.reduce((a, b) => a + b, 0);
            const percentage = ((value / total) * 100).toFixed(1);
            return `${label}: ${value} items (${percentage}%)`;
          }
        }
      }
    },
  };

  // 2. Donation Trends (Bar Chart)
  const donationTrendData = {
    labels: chartData.donation_trends.map(d => new Date(d.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })),
    datasets: [{
      label: 'Donations',
      data: chartData.donation_trends.map(d => d.count),
      backgroundColor: 'rgba(59, 130, 246, 0.8)',
      borderColor: 'rgba(59, 130, 246, 1)',
      borderWidth: 1,
      borderRadius: 6,
    }],
  };

  const donationTrendOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: 'Donation Trends (Last 30 Days)',
        font: {
          size: 18,
          weight: 'bold',
        },
        padding: {
          top: 10,
          bottom: 20,
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 1,
        },
      },
    },
  };

  // 3. Expiry Status Distribution (Doughnut Chart)
  const expiryChartData = {
    labels: chartData.expiry_distribution.map(e => e.status),
    datasets: [{
      label: 'Items',
      data: chartData.expiry_distribution.map(e => e.count),
      backgroundColor: chartData.expiry_distribution.map(e => expiryColors[e.status] || 'rgba(156, 163, 175, 0.8)'),
      borderColor: 'rgba(255, 255, 255, 1)',
      borderWidth: 2,
    }],
  };

  const expiryOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right',
        labels: {
          padding: 15,
          font: {
            size: 12,
          },
        },
      },
      title: {
        display: true,
        text: 'Item Expiry Status',
        font: {
          size: 18,
          weight: 'bold',
        },
        padding: {
          top: 10,
          bottom: 20,
        },
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const label = context.label || '';
            const value = context.parsed || 0;
            const total = context.dataset.data.reduce((a, b) => a + b, 0);
            const percentage = ((value / total) * 100).toFixed(1);
            return `${label}: ${value} items (${percentage}%)`;
          }
        }
      }
    },
  };

  // 4. Top Donors (Horizontal Bar Chart)
  const topDonorsData = {
    labels: chartData.top_donors.map(d => d.name),
    datasets: [{
      label: 'Items Donated',
      data: chartData.top_donors.map(d => d.item_count),
      backgroundColor: 'rgba(139, 92, 246, 0.8)',
      borderColor: 'rgba(139, 92, 246, 1)',
      borderWidth: 1,
      borderRadius: 6,
    }],
  };

  const topDonorsOptions = {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: 'Top 5 Donors by Item Count',
        font: {
          size: 18,
          weight: 'bold',
        },
        padding: {
          top: 10,
          bottom: 20,
        },
      },
    },
    scales: {
      x: {
        beginAtZero: true,
        ticks: {
          stepSize: 1,
        },
      },
    },
  };

  return (
    <div className="charts-container">
      <div className="charts-header">
        <h2>📊 Analytics & Insights</h2>
        <p>Visual representation of key metrics and trends</p>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <div className="chart-wrapper">
            <Pie data={categoryChartData} options={categoryOptions} />
          </div>
        </div>

        <div className="chart-card">
          <div className="chart-wrapper">
            <Doughnut data={expiryChartData} options={expiryOptions} />
          </div>
        </div>

        <div className="chart-card chart-wide">
          <div className="chart-wrapper">
            <Bar data={donationTrendData} options={donationTrendOptions} />
          </div>
        </div>

        <div className="chart-card chart-wide">
          <div className="chart-wrapper">
            <Bar data={topDonorsData} options={topDonorsOptions} />
          </div>
        </div>
      </div>
    </div>
  );
}
