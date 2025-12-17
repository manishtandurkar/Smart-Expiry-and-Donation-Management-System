import React, { useState, useEffect } from 'react';
import { statsAPI, alertsAPI } from '../services/api';
import './Dashboard.css';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [checking, setChecking] = useState(false);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await statsAPI.getDashboard();
      setStats(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch statistics');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleExpiryCheck = async () => {
    try {
      setChecking(true);
      await alertsAPI.triggerCheck(30);
      alert('Expiry check completed! Check alerts page for results.');
      fetchStats(); // Refresh stats
    } catch (err) {
      alert('Failed to run expiry check');
      console.error(err);
    } finally {
      setChecking(false);
    }
  };

  if (loading) return (
    <div className="dashboard">
      <div className="loading-state">
        <div className="spinner-large"></div>
        <p>Loading dashboard...</p>
      </div>
    </div>
  );
  if (error) return <div className="error">{error}</div>;
  if (!stats) return null;

  return (
    <div className="dashboard">
      <div className="hero-section">
        <div className="hero-content">
          <div className="hero-badge">📊 Smart Analytics</div>
          <h1 className="hero-title">Inventory Command Center</h1>
          <p className="hero-subtitle">Real-time insights across stock, donations, and expiry management</p>
          <div className="hero-actions">
            <button 
              onClick={handleExpiryCheck} 
              disabled={checking}
              className="btn-primary"
            >
              {checking ? (
                <><span className="spinner"></span> Checking...</>
              ) : (
                <><span className="icon">🔍</span> Run Expiry Check</>
              )}
            </button>
            <div className="stats-summary">
              <span className="summary-item">{stats.total_items} Items</span>
              <span className="divider">•</span>
              <span className="summary-item">{stats.total_donors} Donors</span>
            </div>
          </div>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card card-blue">
          <div className="stat-header">
            <span className="stat-icon">📦</span>
            <span className="stat-badge">Inventory</span>
          </div>
          <div className="stat-value">{stats.total_items}</div>
          <div className="stat-label">Total Items</div>
        </div>

        <div className="stat-card card-purple">
          <div className="stat-header">
            <span className="stat-icon">👥</span>
            <span className="stat-badge">Network</span>
          </div>
          <div className="stat-value">{stats.total_donors}</div>
          <div className="stat-label">Active Donors</div>
        </div>

        <div className="stat-card card-teal">
          <div className="stat-header">
            <span className="stat-icon">🏢</span>
            <span className="stat-badge">Partners</span>
          </div>
          <div className="stat-value">{stats.total_receivers}</div>
          <div className="stat-label">Receivers</div>
        </div>

        <div className="stat-card card-indigo">
          <div className="stat-header">
            <span className="stat-icon">🎁</span>
            <span className="stat-badge">Impact</span>
          </div>
          <div className="stat-value">{stats.total_donations}</div>
          <div className="stat-label">Total Donations</div>
        </div>

        <div className="stat-card card-warning">
          <div className="stat-header">
            <span className="stat-icon">⚠️</span>
            <span className="stat-badge warning">Watch List</span>
          </div>
          <div className="stat-value">{stats.expiring_soon}</div>
          <div className="stat-label">Expiring Soon (7d)</div>
        </div>

        <div className="stat-card card-danger">
          <div className="stat-header">
            <span className="stat-icon">❌</span>
            <span className="stat-badge danger">Critical</span>
          </div>
          <div className="stat-value">{stats.expired_items}</div>
          <div className="stat-label">Expired Items</div>
        </div>

        <div className="stat-card card-orange">
          <div className="stat-header">
            <span className="stat-icon">🔔</span>
            <span className="stat-badge alert">Pending</span>
          </div>
          <div className="stat-value">{stats.total_alerts}</div>
          <div className="stat-label">Active Alerts</div>
        </div>

        <div className="stat-card card-cyan">
          <div className="stat-header">
            <span className="stat-icon">📉</span>
            <span className="stat-badge info">Restock</span>
          </div>
          <div className="stat-value">{stats.low_stock_items}</div>
          <div className="stat-label">Low Stock (≤10)</div>
        </div>
      </div>

      <div className="features-section">
        <div className="section-header">
          <h2>💡 System Capabilities</h2>
          <p>Built for academic excellence with enterprise-grade features</p>
        </div>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🗄️</div>
            <h3>Hybrid Database</h3>
            <p>MySQL + MongoDB dual-write architecture for ACID + flexibility</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🔔</div>
            <h3>Smart Alerts</h3>
            <p>Automated expiry detection with multi-database logging</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🤖</div>
            <h3>NLP Classification</h3>
            <p>AI-powered category prediction using TextBlob</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>Real-Time Tracking</h3>
            <p>Live inventory updates with complete audit trails</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
