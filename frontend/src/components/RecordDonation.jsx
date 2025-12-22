import React, { useState, useEffect } from 'react';
import { donationsAPI, itemsAPI, receiversAPI, donorsAPI } from '../services/api';
import './RecordDonation.css';

function RecordDonation() {
  const [formData, setFormData] = useState({
    item_id: '',
    receiver_id: '',
    donor_id: '',
    quantity: '',
    delivery_mode: '',
    delivered_by: '',
    notes: '',
  });

  const [items, setItems] = useState([]);
  const [receivers, setReceivers] = useState([]);
  const [donors, setDonors] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [itemsRes, receiversRes, donorsRes] = await Promise.all([
        itemsAPI.getAll(),
        receiversAPI.getAll(),
        donorsAPI.getAll(),
      ]);
      setItems(itemsRes.data);
      setReceivers(receiversRes.data);
      setDonors(donorsRes.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      const data = {
        item_id: parseInt(formData.item_id),
        receiver_id: parseInt(formData.receiver_id),
        donor_id: formData.donor_id ? parseInt(formData.donor_id) : null,
        quantity: parseInt(formData.quantity),
        delivery_mode: formData.delivery_mode || null,
        delivered_by: formData.delivered_by || null,
        notes: formData.notes || null,
      };

      await donationsAPI.create(data);
      alert('Donation recorded successfully!');
      
      setFormData({
        item_id: '',
        receiver_id: '',
        donor_id: '',
        quantity: '',
        delivery_mode: '',
        delivered_by: '',
        notes: '',
      });
      fetchData(); // Refresh items
    } catch (err) {
      alert('Failed to record donation: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const selectedItem = items.find(i => i.item_id === parseInt(formData.item_id));

  return (
    <div className="record-donation">
      <h1>🎁 Record Donation</h1>

      <form onSubmit={handleSubmit} className="donation-form">
        <div className="form-group">
          <label>Select Item *</label>
          <select
            name="item_id"
            value={formData.item_id}
            onChange={handleChange}
            required
          >
            <option value="">Choose an item</option>
            {items.map(item => (
              <option key={item.item_id} value={item.item_id}>
                {item.name} (Available: {item.quantity})
              </option>
            ))}
          </select>
          {selectedItem && (
            <div className="item-info">
              Expiry: {new Date(selectedItem.expiry_date).toLocaleDateString()} | 
              Category: {selectedItem.category || 'N/A'}
            </div>
          )}
        </div>

        <div className="form-group">
          <label>Select Receiver *</label>
          <select
            name="receiver_id"
            value={formData.receiver_id}
            onChange={handleChange}
            required
          >
            <option value="">Choose a receiver</option>
            {receivers.map(receiver => (
              <option key={receiver.receiver_id} value={receiver.receiver_id}>
                {receiver.name} ({receiver.region || 'No region'})
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Approving Donor (Optional)</label>
          <select
            name="donor_id"
            value={formData.donor_id}
            onChange={handleChange}
          >
            <option value="">Select approving donor (optional)</option>
            {donors.map(donor => (
              <option key={donor.donor_id} value={donor.donor_id}>
                {donor.name}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Quantity *</label>
          <input
            type="number"
            name="quantity"
            value={formData.quantity}
            onChange={handleChange}
            required
            min="1"
            max={selectedItem?.quantity || undefined}
            placeholder="Enter quantity"
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Delivery Mode</label>
            <input
              type="text"
              name="delivery_mode"
              value={formData.delivery_mode}
              onChange={handleChange}
              placeholder="e.g., Pickup, Courier, Self-delivery"
            />
          </div>

          <div className="form-group">
            <label>Delivered By</label>
            <input
              type="text"
              name="delivered_by"
              value={formData.delivered_by}
              onChange={handleChange}
              placeholder="Person or service name"
            />
          </div>
        </div>

        <div className="form-group">
          <label>Notes</label>
          <textarea
            name="notes"
            value={formData.notes}
            onChange={handleChange}
            rows="3"
            placeholder="Additional notes about this donation..."
          />
        </div>

        <button type="submit" disabled={loading} className="btn-submit">
          {loading ? 'Recording...' : '✓ Record Donation'}
        </button>
      </form>
    </div>
  );
}

export default RecordDonation;
