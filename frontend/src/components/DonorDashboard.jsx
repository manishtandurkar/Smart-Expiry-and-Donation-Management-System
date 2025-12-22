import React, { useState, useEffect } from 'react';
import { itemsAPI } from '../services/api';
import './DonorDashboard.css';

function DonorDashboard({ user, donorId, onLogout }) {
  const [activeTab, setActiveTab] = useState('add');
  const [formData, setFormData] = useState({
    name: '',
    quantity: '',
    expiry_date: '',
    description: '',
    storage_condition: '',
    category: '',
  });
  const [myItems, setMyItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState(null);

  const categories = ["Food", "Medicine", "Clothing", "Hygiene", "Stationery", "Electronics"];

  useEffect(() => {
    if (activeTab === 'myitems') {
      fetchMyItems();
    }
  }, [activeTab]);

  const fetchMyItems = async () => {
    try {
      setLoading(true);
      const response = await itemsAPI.getAll({ donor_id: donorId });
      setMyItems(response.data);
    } catch (err) {
      console.error('Failed to fetch items', err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handlePredictCategory = async () => {
    if (!formData.name) {
      alert('Please enter the item name first');
      return;
    }

    try {
      const response = await itemsAPI.predictCategory(formData.name);
      setPrediction(response.data);
      setFormData({ ...formData, category: response.data.predicted_category });
    } catch (err) {
      console.error('Prediction failed', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      const data = {
        ...formData,
        quantity: parseInt(formData.quantity),
        donor_id: donorId,
      };

      await itemsAPI.create(data);
      alert('Item added successfully! It is now available in the common inventory.');
      
      setFormData({
        name: '',
        quantity: '',
        expiry_date: '',
        description: '',
        storage_condition: '',
        category: '',
      });
      setPrediction(null);
    } catch (err) {
      alert('Failed to add item: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
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

  return (
    <div className="donor-dashboard">
      <header className="dashboard-header">
        <div className="header-left">
          <h1>🎁 Donor Dashboard</h1>
          <p>Welcome, {user.name}!</p>
        </div>
        <button className="logout-btn" onClick={onLogout}>Logout</button>
      </header>

      <nav className="dashboard-nav">
        <button 
          className={activeTab === 'add' ? 'active' : ''} 
          onClick={() => setActiveTab('add')}
        >
          ➕ Add Item
        </button>
        <button 
          className={activeTab === 'myitems' ? 'active' : ''} 
          onClick={() => setActiveTab('myitems')}
        >
          📦 My Donations
        </button>
      </nav>

      <main className="dashboard-content">
        {activeTab === 'add' && (
          <div className="add-item-section">
            <h2>Add New Item to Donate</h2>
            <p className="section-desc">Items you add will be available in the common inventory for receivers to request.</p>

            <form onSubmit={handleSubmit} className="item-form">
              <div className="form-row">
                <div className="form-group">
                  <label>Item Name *</label>
                  <div className="input-with-button">
                    <input
                      type="text"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      placeholder="e.g., Rice Bags, Paracetamol"
                      required
                    />
                    <button type="button" onClick={handlePredictCategory} className="predict-btn">
                      🤖 Auto Category
                    </button>
                  </div>
                </div>

                <div className="form-group">
                  <label>Quantity *</label>
                  <input
                    type="number"
                    name="quantity"
                    value={formData.quantity}
                    onChange={handleChange}
                    min="1"
                    placeholder="Enter quantity"
                    required
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Expiry Date *</label>
                  <input
                    type="date"
                    name="expiry_date"
                    value={formData.expiry_date}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Category *</label>
                  <select
                    name="category"
                    value={formData.category}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Select category</option>
                    {categories.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                  {prediction && (
                    <small className="prediction-info">
                      AI predicted: {prediction.predicted_category} ({Math.round(prediction.confidence * 100)}% confidence)
                    </small>
                  )}
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Storage Condition</label>
                  <input
                    type="text"
                    name="storage_condition"
                    value={formData.storage_condition}
                    onChange={handleChange}
                    placeholder="e.g., Cool and dry place"
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Description</label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  placeholder="Additional details about the item..."
                  rows="3"
                />
              </div>

              <button type="submit" className="submit-btn" disabled={loading}>
                {loading ? 'Adding...' : '➕ Add Item to Inventory'}
              </button>
            </form>
          </div>
        )}

        {activeTab === 'myitems' && (
          <div className="my-items-section">
            <h2>My Donated Items ({myItems.length})</h2>
            <p className="section-desc">Items you have added to the inventory</p>

            {loading ? (
              <div className="loading">Loading...</div>
            ) : myItems.length === 0 ? (
              <div className="empty-state">
                <p>You haven't donated any items yet.</p>
                <button onClick={() => setActiveTab('add')}>Add Your First Item</button>
              </div>
            ) : (
              <div className="items-table">
                <table>
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Category</th>
                      <th>Quantity</th>
                      <th>Expiry Date</th>
                      <th>Days Left</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {myItems.map(item => (
                      <tr key={item.item_id}>
                        <td><strong>{item.name}</strong></td>
                        <td>{item.category || 'N/A'}</td>
                        <td>{item.quantity}</td>
                        <td>{new Date(item.expiry_date).toLocaleDateString()}</td>
                        <td>{item.days_until_expiry}</td>
                        <td>
                          <span className={`status-badge ${getStatusClass(item.expiry_status)}`}>
                            {item.expiry_status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default DonorDashboard;
