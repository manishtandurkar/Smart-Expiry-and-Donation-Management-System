import React, { useEffect, useState } from 'react';
import { donorsAPI, receiversAPI, authAPI, requestsAPI, statsAPI, itemsAPI, donationsAPI } from '../services/api';
import './AdminDashboard.css';

export default function Admin({ user, onLogout }) {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [donors, setDonors] = useState([]);
  const [receivers, setReceivers] = useState([]);
  const [requests, setRequests] = useState([]);
  const [items, setItems] = useState([]);
  const [donations, setDonations] = useState([]);
  const [loading, setLoading] = useState(false);

  // New user form
  const [newUser, setNewUser] = useState({
    username: '',
    password: '',
    name: '',
    role: 'donor',
    contact: '',
    address: '',
  });

  const [confirmState, setConfirmState] = useState(null);

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'dashboard') {
        const res = await statsAPI.getDashboard();
        setStats(res.data);
      } else if (activeTab === 'users') {
        const [usersRes, donorsRes, receiversRes] = await Promise.all([
          authAPI.getUsers(),
          donorsAPI.getAll(),
          receiversAPI.getAll(),
        ]);
        setUsers(usersRes.data);
        setDonors(donorsRes.data);
        setReceivers(receiversRes.data);
      } else if (activeTab === 'requests') {
        const res = await requestsAPI.getAll();
        setRequests(res.data);
      } else if (activeTab === 'items') {
        const res = await itemsAPI.getAll();
        setItems(res.data);
      } else if (activeTab === 'donations') {
        const res = await donationsAPI.getAll();
        setDonations(res.data);
      }
    } catch (err) {
      console.error('Error fetching data', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    try {
      await authAPI.register(newUser);
      alert(`${newUser.role.charAt(0).toUpperCase() + newUser.role.slice(1)} account created successfully!`);
      setNewUser({
        username: '',
        password: '',
        name: '',
        role: 'donor',
        contact: '',
        address: '',
      });
      fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || err.message);
    }
  };

  const handleDeleteUser = async (userId, name) => {
    setConfirmState({ type: 'user', id: userId, name });
  };

  const confirmDelete = async () => {
    try {
      if (confirmState.type === 'user') {
        await authAPI.deleteUser(confirmState.id);
      }
      setConfirmState(null);
      fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || err.message);
    }
  };

  const handleRequestAction = async (requestId, action) => {
    try {
      await requestsAPI.update(requestId, {
        status: action,
        admin_notes: action === 'approved' ? 'Approved by admin' : 'Rejected by admin',
      });
      alert(`Request ${action} successfully!`);
      fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || err.message);
    }
  };

  const getRequestStatusClass = (status) => {
    switch(status) {
      case 'approved': return 'req-approved';
      case 'rejected': return 'req-rejected';
      default: return 'req-pending';
    }
  };

  const getExpiryStatusClass = (status) => {
    switch(status?.toUpperCase()) {
      case 'EXPIRED': return 'status-expired';
      case 'CRITICAL': return 'status-critical';
      case 'WARNING': return 'status-warning';
      default: return 'status-safe';
    }
  };

  return (
    <div className="admin-dashboard">
      <header className="dashboard-header">
        <div className="header-left">
          <h1>⚙️ Admin Dashboard</h1>
          <p>Welcome, {user.name}!</p>
        </div>
        <button className="logout-btn" onClick={onLogout}>Logout</button>
      </header>

      <nav className="dashboard-nav">
        <button 
          className={activeTab === 'dashboard' ? 'active' : ''} 
          onClick={() => setActiveTab('dashboard')}
        >
          📊 Overview
        </button>
        <button 
          className={activeTab === 'items' ? 'active' : ''} 
          onClick={() => setActiveTab('items')}
        >
          📦 All Items
        </button>
        <button 
          className={activeTab === 'donations' ? 'active' : ''} 
          onClick={() => setActiveTab('donations')}
        >
          🤝 Donation History
        </button>
        <button 
          className={activeTab === 'requests' ? 'active' : ''} 
          onClick={() => setActiveTab('requests')}
        >
          📋 Requests
        </button>
        <button 
          className={activeTab === 'users' ? 'active' : ''} 
          onClick={() => setActiveTab('users')}
        >
          👥 Manage Users
        </button>
      </nav>

      <main className="dashboard-content">
        {activeTab === 'dashboard' && (
          <div className="overview-section">
            <h2>System Overview</h2>
            {loading ? (
              <div className="loading">Loading statistics...</div>
            ) : stats && (
              <div className="stats-grid">
                <div className="stat-card">
                  <span className="stat-icon">📦</span>
                  <div className="stat-info">
                    <h3>{stats.total_items}</h3>
                    <p>Total Items</p>
                  </div>
                </div>
                <div className="stat-card">
                  <span className="stat-icon">🎁</span>
                  <div className="stat-info">
                    <h3>{stats.total_donors}</h3>
                    <p>Donors</p>
                  </div>
                </div>
                <div className="stat-card">
                  <span className="stat-icon">🏢</span>
                  <div className="stat-info">
                    <h3>{stats.total_receivers}</h3>
                    <p>Receivers</p>
                  </div>
                </div>
                <div className="stat-card">
                  <span className="stat-icon">🤝</span>
                  <div className="stat-info">
                    <h3>{stats.total_donations}</h3>
                    <p>Donations</p>
                  </div>
                </div>
                <div className="stat-card warning">
                  <span className="stat-icon">⚠️</span>
                  <div className="stat-info">
                    <h3>{stats.expiring_soon}</h3>
                    <p>Expiring Soon</p>
                  </div>
                </div>
                <div className="stat-card danger">
                  <span className="stat-icon">🔔</span>
                  <div className="stat-info">
                    <h3>{stats.total_alerts}</h3>
                    <p>Active Alerts</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'items' && (
          <div className="items-section">
            <h2>All Items in Inventory ({items.length})</h2>
            <p className="section-desc">Complete details of all items in the system</p>

            {loading ? (
              <div className="loading">Loading items...</div>
            ) : items.length === 0 ? (
              <div className="empty-state">
                <p>No items in inventory.</p>
              </div>
            ) : (
              <div className="items-table-container">
                <table className="items-table">
                  <thead>
                    <tr>
                      <th>Item Name</th>
                      <th>Category</th>
                      <th>Quantity</th>
                      <th>Expiry Date</th>
                      <th>Days Left</th>
                      <th>Status</th>
                      <th>Donor</th>
                      <th>Storage</th>
                    </tr>
                  </thead>
                  <tbody>
                    {items.map(item => (
                      <tr key={item.item_id}>
                        <td><strong>{item.name}</strong></td>
                        <td>{item.category || 'N/A'}</td>
                        <td>{item.quantity} units</td>
                        <td>{new Date(item.expiry_date).toLocaleDateString()}</td>
                        <td>{item.days_until_expiry} days</td>
                        <td>
                          <span className={`status-badge ${getExpiryStatusClass(item.expiry_status)}`}>
                            {item.expiry_status}
                          </span>
                        </td>
                        <td>{item.donor?.name}</td>
                        <td>{item.storage_condition || 'N/A'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === 'donations' && (
          <div className="donations-section">
            <div className="section-header">
              <div>
                <h2>Donation History</h2>
                <p className="section-desc">Complete history of all donations made in the system</p>
              </div>
            </div>

            {loading ? (
              <div className="loading">Loading donations...</div>
            ) : donations.length === 0 ? (
              <div className="empty-state">
                <p>No donations recorded yet.</p>
              </div>
            ) : (
              <>
                {/* Summary Statistics */}
                <div className="donation-stats">
                  <div className="stat-box">
                    <span className="stat-label">Total Donations</span>
                    <span className="stat-value">{donations.length}</span>
                  </div>
                  <div className="stat-box">
                    <span className="stat-label">Total Items Donated</span>
                    <span className="stat-value">
                      {donations.reduce((sum, d) => sum + d.quantity, 0)} units
                    </span>
                  </div>
                  <div className="stat-box">
                    <span className="stat-label">Unique Donors</span>
                    <span className="stat-value">
                      {new Set(donations.map(d => d.approving_donor?.donor_id || d.item?.donor?.donor_id).filter(Boolean)).size}
                    </span>
                  </div>
                  <div className="stat-box">
                    <span className="stat-label">Unique Receivers</span>
                    <span className="stat-value">
                      {new Set(donations.map(d => d.receiver?.receiver_id).filter(Boolean)).size}
                    </span>
                  </div>
                </div>

                {/* Donations List as Cards */}
                <div className="donations-grid">
                  {donations
                    .sort((a, b) => new Date(b.donation_date) - new Date(a.donation_date))
                    .map(donation => (
                      <div key={donation.donation_id} className="donation-card">
                        <div className="donation-header">
                          <div className="donation-title">
                            <h4>📦 {donation.item?.name}</h4>
                            <span className="donation-date">
                              {new Date(donation.donation_date).toLocaleDateString('en-US', {
                                year: 'numeric',
                                month: 'short',
                                day: 'numeric'
                              })}
                            </span>
                          </div>
                          <div className="donation-quantity">
                            <span className="quantity-badge">{donation.quantity} units</span>
                          </div>
                        </div>
                        
                        <div className="donation-details">
                          <div className="detail-row">
                            <span className="detail-label">🎁 From:</span>
                            <span className="detail-value">{donation.approving_donor?.name || donation.item?.donor?.name || 'N/A'}</span>
                          </div>
                          <div className="detail-row">
                            <span className="detail-label">🏢 To:</span>
                            <span className="detail-value">{donation.receiver?.name || 'N/A'}</span>
                          </div>
                          {donation.delivery_mode && (
                            <div className="detail-row">
                              <span className="detail-label">🚚 Delivery:</span>
                              <span className="detail-value">{donation.delivery_mode}</span>
                            </div>
                          )}
                          {donation.delivered_by && (
                            <div className="detail-row">
                              <span className="detail-label">👤 Delivered by:</span>
                              <span className="detail-value">{donation.delivered_by}</span>
                            </div>
                          )}
                          {donation.notes && (
                            <div className="detail-row notes">
                              <span className="detail-label">📝 Notes:</span>
                              <span className="detail-value">{donation.notes}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                </div>
              </>
            )}
          </div>
        )}

        {activeTab === 'users' && (
          <div className="users-section">
            <div className="create-user-card">
              <h3>Create New User</h3>
              <form onSubmit={handleCreateUser} className="user-form">
                <div className="form-row">
                  <div className="form-group">
                    <label>Role *</label>
                    <select
                      value={newUser.role}
                      onChange={e => setNewUser({ ...newUser, role: e.target.value })}
                      required
                    >
                      <option value="donor">Donor</option>
                      <option value="receiver">Receiver</option>
                      <option value="admin">Admin</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Username *</label>
                    <input
                      type="text"
                      value={newUser.username}
                      onChange={e => setNewUser({ ...newUser, username: e.target.value })}
                      placeholder="Login username"
                      required
                    />
                  </div>
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label>Password *</label>
                    <input
                      type="password"
                      value={newUser.password}
                      onChange={e => setNewUser({ ...newUser, password: e.target.value })}
                      placeholder="Login password"
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Full Name *</label>
                    <input
                      type="text"
                      value={newUser.name}
                      onChange={e => setNewUser({ ...newUser, name: e.target.value })}
                      placeholder="Organization/Person name"
                      required
                    />
                  </div>
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label>Contact</label>
                    <input
                      type="text"
                      value={newUser.contact}
                      onChange={e => setNewUser({ ...newUser, contact: e.target.value })}
                      placeholder="Phone number"
                    />
                  </div>
                  <div className="form-group">
                    <label>Address</label>
                    <input
                      type="text"
                      value={newUser.address}
                      onChange={e => setNewUser({ ...newUser, address: e.target.value })}
                      placeholder="Full address"
                    />
                  </div>
                </div>
                <button type="submit" className="create-btn">➕ Create User</button>
              </form>
            </div>

            <div className="users-list">
              <h3>All Users ({users.length})</h3>
              {loading ? (
                <div className="loading">Loading users...</div>
              ) : (
                <table className="users-table">
                  <thead>
                    <tr>
                      <th>Username</th>
                      <th>Name</th>
                      <th>Role</th>
                      <th>Contact</th>
                      <th>Created</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map(u => (
                      <tr key={u.user_id}>
                        <td><code>{u.username}</code></td>
                        <td><strong>{u.name}</strong></td>
                        <td>
                          <span className={`role-badge role-${u.role}`}>
                            {u.role.toUpperCase()}
                          </span>
                        </td>
                        <td>{u.contact || '-'}</td>
                        <td>{new Date(u.created_at).toLocaleDateString()}</td>
                        <td>
                          {u.role !== 'admin' && (
                            <button 
                              className="delete-btn"
                              onClick={() => handleDeleteUser(u.user_id, u.name)}
                            >
                              Delete
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        )}

        {activeTab === 'requests' && (
          <div className="requests-section">
            <h2>Donation Requests ({requests.length})</h2>
            <p className="section-desc">Review and approve/reject donation requests from receivers</p>

            {loading ? (
              <div className="loading">Loading requests...</div>
            ) : requests.length === 0 ? (
              <div className="empty-state">
                <p>No donation requests at this time.</p>
              </div>
            ) : (
              <div className="requests-list">
                {requests.map(req => (
                  <div key={req.request_id} className={`request-card ${req.status}`}>
                    <div className="request-header">
                      <div>
                        <h4>{req.item?.name || req.item_name}</h4>
                        <span className={`req-type ${req.request_type}`}>
                          {req.request_type === 'new' ? '🆕 New Item Request' : '📦 Existing Item'}
                        </span>
                      </div>
                      <span className={`req-status ${getRequestStatusClass(req.status)}`}>
                        {req.status.toUpperCase()}
                      </span>
                    </div>
                    <div className="request-body">
                      <p><strong>Receiver:</strong> {req.receiver?.name}</p>
                      <p><strong>Quantity:</strong> {req.quantity}</p>
                      {req.notes && <p><strong>Notes:</strong> {req.notes}</p>}
                      <p><strong>Requested:</strong> {new Date(req.created_at).toLocaleString()}</p>
                    </div>
                    {req.status === 'pending' && (
                      <div className="request-actions">
                        <button 
                          className="approve-btn"
                          onClick={() => handleRequestAction(req.request_id, 'approved')}
                        >
                          ✅ Approve
                        </button>
                        <button 
                          className="reject-btn"
                          onClick={() => handleRequestAction(req.request_id, 'rejected')}
                        >
                          ❌ Reject
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>

      {/* Confirmation Modal */}
      {confirmState && (
        <div className="modal-backdrop">
          <div className="modal-card">
            <h4>Confirm Delete</h4>
            <p>Are you sure you want to delete "{confirmState.name}"?</p>
            <div className="modal-actions">
              <button onClick={() => setConfirmState(null)} className="cancel-btn">Cancel</button>
              <button onClick={confirmDelete} className="danger-btn">Delete</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
