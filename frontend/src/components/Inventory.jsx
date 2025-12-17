import React, { useState, useEffect } from 'react';
import { itemsAPI } from '../services/api';
import './Inventory.css';

function Inventory() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sortAsc, setSortAsc] = useState(true); // true => nearest expiry first

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    try {
      const response = await itemsAPI.getAll();
      // Default sort: nearest expiry first (ascending)
      const sorted = response.data.slice().sort((a, b) => new Date(a.expiry_date) - new Date(b.expiry_date));
      setItems(sorted);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const toggleOrder = () => {
    setItems(prev => prev.slice().reverse());
    setSortAsc(s => !s);
  };

  const getStatusClass = (status) => {
    switch(status) {
      case 'EXPIRED': return 'status-expired';
      case 'CRITICAL': return 'status-critical';
      case 'WARNING': return 'status-warning';
      default: return 'status-safe';
    }
  };

  if (loading) return <div className="loading">Loading inventory...</div>;

  return (
    <div className="inventory">
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <h1>📦 Inventory ({items.length} items)</h1>
        <button className="sort-toggle" onClick={toggleOrder}>
          {sortAsc ? 'Show Furthest First' : 'Show Nearest First'}
        </button>
      </div>
      
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Category</th>
              <th>Quantity</th>
              <th>Expiry Date</th>
              <th>Days Left</th>
              <th>Status</th>
              <th>Donor</th>
            </tr>
          </thead>
          <tbody>
            {items.map(item => (
              <tr key={item.item_id}>
                <td>{item.item_id}</td>
                <td><strong>{item.name}</strong></td>
                <td>{item.category.category_name}</td>
                <td>{item.quantity}</td>
                <td>{new Date(item.expiry_date).toLocaleDateString()}</td>
                <td>{item.days_until_expiry}</td>
                <td>
                  <span className={`status-badge ${getStatusClass(item.expiry_status)}`}>
                    {item.expiry_status}
                  </span>
                </td>
                <td>{item.donor.name}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Inventory;
