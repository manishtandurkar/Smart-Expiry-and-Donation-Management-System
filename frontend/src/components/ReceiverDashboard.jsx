import React, { useState, useEffect } from 'react';
import { itemsAPI, requestsAPI } from '../services/api';
import './ReceiverDashboard.css';

function ReceiverDashboard({ user, receiverId, onLogout }) {
  const [activeTab, setActiveTab] = useState('inventory');
  const [items, setItems] = useState([]);
  const [myRequests, setMyRequests] = useState([]);
  const [approvedRequests, setApprovedRequests] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Request form
  const [requestModal, setRequestModal] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [requestQuantity, setRequestQuantity] = useState('');
  const [requestNotes, setRequestNotes] = useState('');
  
  // New item request form
  const [newItemModal, setNewItemModal] = useState(false);
  const [newItemName, setNewItemName] = useState('');
  const [newItemQuantity, setNewItemQuantity] = useState('');
  const [newItemNotes, setNewItemNotes] = useState('');

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'inventory') {
        const response = await itemsAPI.getAll();
        setItems(response.data);
      } else if (activeTab === 'myrequests') {
        const response = await requestsAPI.getByReceiver(receiverId);
        setMyRequests(response.data);
      } else if (activeTab === 'approved') {
        const response = await requestsAPI.getApproved(receiverId);
        setApprovedRequests(response.data);
      }
    } catch (err) {
      console.error('Failed to fetch data', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRequestItem = (item) => {
    setSelectedItem(item);
    setRequestQuantity('');
    setRequestNotes('');
    setRequestModal(true);
  };

  const submitRequest = async () => {
    if (!requestQuantity || parseInt(requestQuantity) <= 0) {
      alert('Please enter a valid quantity');
      return;
    }

    if (parseInt(requestQuantity) > selectedItem.quantity) {
      alert(`Cannot request more than available quantity (${selectedItem.quantity})`);
      return;
    }

    try {
      await requestsAPI.create({
        receiver_id: receiverId,
        item_id: selectedItem.item_id,
        quantity: parseInt(requestQuantity),
        request_type: 'existing',
        notes: requestNotes,
      });
      alert('Request submitted successfully! Waiting for admin approval.');
      setRequestModal(false);
      fetchData();
    } catch (err) {
      alert('Failed to submit request: ' + (err.response?.data?.detail || err.message));
    }
  };

  const submitNewItemRequest = async () => {
    if (!newItemName.trim()) {
      alert('Please enter the item name');
      return;
    }
    if (!newItemQuantity || parseInt(newItemQuantity) <= 0) {
      alert('Please enter a valid quantity');
      return;
    }

    try {
      await requestsAPI.create({
        receiver_id: receiverId,
        item_name: newItemName,
        quantity: parseInt(newItemQuantity),
        request_type: 'new',
        notes: newItemNotes,
      });
      alert('New item request submitted! Admin will review your request.');
      setNewItemModal(false);
      setNewItemName('');
      setNewItemQuantity('');
      setNewItemNotes('');
      fetchData();
    } catch (err) {
      alert('Failed to submit request: ' + (err.response?.data?.detail || err.message));
    }
  };

  const getStatusClass = (status) => {
    switch(status) {
      case 'EXPIRED': return 'status-expired';
      case 'CRITICAL': return 'status-critical';
      case 'WARNING': return 'status-warning';
      default: return 'status-safe';
    }
  };

  const getRequestStatusClass = (status) => {
    switch(status) {
      case 'approved': return 'req-approved';
      case 'rejected': return 'req-rejected';
      default: return 'req-pending';
    }
  };

  return (
    <div className="receiver-dashboard">
      <header className="dashboard-header">
        <div className="header-left">
          <h1>🏢 Receiver Dashboard</h1>
          <p>Welcome, {user.name}!</p>
        </div>
        <button className="logout-btn" onClick={onLogout}>Logout</button>
      </header>

      <nav className="dashboard-nav">
        <button 
          className={activeTab === 'inventory' ? 'active' : ''} 
          onClick={() => setActiveTab('inventory')}
        >
          📦 Available Inventory
        </button>
        <button 
          className={activeTab === 'myrequests' ? 'active' : ''} 
          onClick={() => setActiveTab('myrequests')}
        >
          📋 My Requests
        </button>
        <button 
          className={activeTab === 'approved' ? 'active' : ''} 
          onClick={() => setActiveTab('approved')}
        >
          ✅ Approved Items
        </button>
      </nav>

      <main className="dashboard-content">
        {activeTab === 'inventory' && (
          <div className="inventory-section">
            <div className="section-header">
              <div>
                <h2>Available Inventory ({items.length} items)</h2>
                <p className="section-desc">Browse items and request what your organization needs</p>
              </div>
              <button className="new-request-btn" onClick={() => setNewItemModal(true)}>
                ➕ Request New Item
              </button>
            </div>

            {loading ? (
              <div className="loading">Loading inventory...</div>
            ) : items.length === 0 ? (
              <div className="empty-state">
                <p>No items available in inventory.</p>
                <button onClick={() => setNewItemModal(true)}>Request a New Item</button>
              </div>
            ) : (
              <div className="items-table-container">
                <table className="items-table">
                  <thead>
                    <tr>
                      <th>Item Name</th>
                      <th>Available Quantity</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {items.map(item => (
                      <tr key={item.item_id}>
                        <td><strong>{item.name}</strong></td>
                        <td>{item.quantity} units</td>
                        <td>
                          <button 
                            className="request-btn"
                            onClick={() => handleRequestItem(item)}
                            disabled={item.quantity === 0}
                          >
                            📝 Request
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === 'myrequests' && (
          <div className="requests-section">
            <h2>My Requests ({myRequests.length})</h2>
            <p className="section-desc">Track the status of your donation requests</p>

            {loading ? (
              <div className="loading">Loading requests...</div>
            ) : myRequests.length === 0 ? (
              <div className="empty-state">
                <p>You haven't made any requests yet.</p>
                <button onClick={() => setActiveTab('inventory')}>Browse Inventory</button>
              </div>
            ) : (
              <div className="requests-table">
                <table>
                  <thead>
                    <tr>
                      <th>Item</th>
                      <th>Type</th>
                      <th>Quantity</th>
                      <th>Status</th>
                      <th>Notes</th>
                      <th>Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {myRequests.map(req => (
                      <tr key={req.request_id}>
                        <td><strong>{req.item?.name || req.item_name}</strong></td>
                        <td>{req.request_type === 'new' ? '🆕 New Item' : '📦 Existing'}</td>
                        <td>{req.quantity}</td>
                        <td>
                          <span className={`req-status ${getRequestStatusClass(req.status)}`}>
                            {req.status.toUpperCase()}
                          </span>
                        </td>
                        <td>{req.admin_notes || req.notes || '-'}</td>
                        <td>{new Date(req.created_at).toLocaleDateString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === 'approved' && (
          <div className="approved-section">
            <h2>Approved Items ({approvedRequests.length})</h2>
            <p className="section-desc">Items approved for your organization - ready to collect!</p>

            {loading ? (
              <div className="loading">Loading approved items...</div>
            ) : approvedRequests.length === 0 ? (
              <div className="empty-state">
                <p>No approved items yet. Your approved requests will appear here.</p>
              </div>
            ) : (
              <div className="approved-grid">
                {approvedRequests.map(req => (
                  <div key={req.request_id} className="approved-card">
                    <div className="approved-icon">✅</div>
                    <h3>{req.item?.name || req.item_name}</h3>
                    <p className="approved-qty">Quantity: {req.quantity}</p>
                    {req.admin_notes && <p className="admin-note">Note: {req.admin_notes}</p>}
                    <p className="approved-date">Approved on: {new Date(req.updated_at).toLocaleDateString()}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>

      {/* Request Modal */}
      {requestModal && (
        <div className="modal-backdrop" onClick={() => setRequestModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <h3>Request Item</h3>
            <div className="modal-item-info">
              <p><strong>{selectedItem?.name}</strong></p>
              <p>Available: {selectedItem?.quantity} units</p>
            </div>
            <div className="form-group">
              <label>Quantity Needed *</label>
              <input
                type="number"
                value={requestQuantity}
                onChange={e => setRequestQuantity(e.target.value)}
                min="1"
                max={selectedItem?.quantity}
                placeholder="Enter quantity"
              />
            </div>
            <div className="form-group">
              <label>Notes (optional)</label>
              <textarea
                value={requestNotes}
                onChange={e => setRequestNotes(e.target.value)}
                placeholder="Why do you need this item?"
                rows="3"
              />
            </div>
            <div className="modal-actions">
              <button className="cancel-btn" onClick={() => setRequestModal(false)}>Cancel</button>
              <button className="submit-btn" onClick={submitRequest}>Submit Request</button>
            </div>
          </div>
        </div>
      )}

      {/* New Item Request Modal */}
      {newItemModal && (
        <div className="modal-backdrop" onClick={() => setNewItemModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <h3>Request New Item</h3>
            <p className="modal-desc">Request an item that's not currently in the inventory</p>
            <div className="form-group">
              <label>Item Name *</label>
              <input
                type="text"
                value={newItemName}
                onChange={e => setNewItemName(e.target.value)}
                placeholder="What item do you need?"
              />
            </div>
            <div className="form-group">
              <label>Quantity Needed *</label>
              <input
                type="number"
                value={newItemQuantity}
                onChange={e => setNewItemQuantity(e.target.value)}
                min="1"
                placeholder="How many do you need?"
              />
            </div>
            <div className="form-group">
              <label>Description / Reason</label>
              <textarea
                value={newItemNotes}
                onChange={e => setNewItemNotes(e.target.value)}
                placeholder="Describe why your organization needs this item..."
                rows="3"
              />
            </div>
            <div className="modal-actions">
              <button className="cancel-btn" onClick={() => setNewItemModal(false)}>Cancel</button>
              <button className="submit-btn" onClick={submitNewItemRequest}>Submit Request</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ReceiverDashboard;
