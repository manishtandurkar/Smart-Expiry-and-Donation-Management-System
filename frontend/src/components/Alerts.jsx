import React, { useState, useEffect } from 'react';
import { alertsAPI } from '../services/api';
import './Alerts.css';

function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [mongoAlerts, setMongoAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const [mysqlRes, mongoRes] = await Promise.all([
        alertsAPI.getAll({ acknowledged: false }),
        alertsAPI.getMongo()
      ]);

      const mysqlList = Array.isArray(mysqlRes.data) ? mysqlRes.data : [];
      const mongoList = (mongoRes.data && mongoRes.data.alerts) ? mongoRes.data.alerts : [];

      // Filter Mongo alerts to only include CRITICAL or HIGH and items with quantity > 0 (if quantity present)
      const filteredMongo = mongoList.filter(m => {
        const sev = (m.severity || '').toUpperCase();
        const okSeverity = sev === 'CRITICAL' || sev === 'HIGH';
        const okQuantity = m.quantity == null ? true : (m.quantity > 0);
        return okSeverity && okQuantity;
      });

      // Normalize both sources to a common shape and merge
      // Filter MySQL alerts to ensure item has quantity > 0
      const normalizedMysql = mysqlList
        .filter(a => a.item && a.item.quantity > 0)
        .map(a => ({
          source: 'mysql',
          id: a.alert_id,
          item_name: a.item?.name || a.item_name || 'Unknown',
          message: a.message,
          severity: a.severity,
          datetime: a.created_at || a.alert_date,
          quantity: a.item?.quantity ?? null,
          category_name: a.item?.category || a.item?.category_name || null,
          days_until_expiry: a.item?.days_until_expiry ?? null,
          raw: a
        }));

      const normalizedMongo = filteredMongo.map((m, idx) => ({
        source: 'mongo',
        id: m._id || idx,
        item_name: m.item_name || m.item?.name || 'Unknown',
        message: m.message,
        severity: m.severity || 'MEDIUM',
        datetime: m.timestamp || m.alert_date,
        quantity: m.quantity ?? null,
        category_name: m.category_name ?? null,
        days_until_expiry: m.days_until_expiry ?? null,
        raw: m
      }));

      const merged = normalizedMysql.concat(normalizedMongo);

      // Sort newest first by datetime
      merged.sort((a, b) => new Date(b.datetime) - new Date(a.datetime));

      setAlerts(merged);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityClass = (severity) => {
    return `severity-${(severity || 'medium').toLowerCase()}`;
  };

  if (loading) return <div className="loading">Loading alerts...</div>;

  return (
    <div className="alerts">
      <div className="alerts-header">
        <h1>🔔 Alerts</h1>
        <div className="alerts-count">{alerts.length} alerts</div>
      </div>

      <div className="alerts-list">
        {alerts.map(alert => (
          <div key={`${alert.source}-${alert.id}`} className="alert-card">
            <div className={`severity-indicator ${getSeverityClass(alert.severity)}`}>
              {alert.severity}
            </div>
            <div className="alert-content">
              <h3>{alert.item_name}</h3>
              <p>{alert.message}</p>
              <div className="alert-meta">
                <span>📅 {new Date(alert.datetime).toLocaleString()}</span>
                <span>📦 Qty: {alert.quantity ?? '-'}</span>
                <span>🏷️ {alert.category_name ?? '-'}</span>
                <span>🔖 {alert.source.toUpperCase()}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Alerts;
