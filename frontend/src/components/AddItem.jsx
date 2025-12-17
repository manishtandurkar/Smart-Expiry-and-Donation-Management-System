import React, { useState, useEffect } from 'react';
import { itemsAPI, categoriesAPI, donorsAPI } from '../services/api';
import './AddItem.css';

function AddItem() {
  const [formData, setFormData] = useState({
    name: '',
    quantity: '',
    expiry_date: '',
    description: '',
    storage_condition: '',
    category_id: '',
    donor_id: '',
  });

  const [categories, setCategories] = useState([]);
  const [donors, setDonors] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [predicting, setPredicting] = useState(false);

  useEffect(() => {
    fetchCategories();
    fetchDonors();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await categoriesAPI.getAll();
      setCategories(response.data);
    } catch (err) {
      console.error('Failed to fetch categories', err);
    }
  };

  const fetchDonors = async () => {
    try {
      const response = await donorsAPI.getAll();
      setDonors(response.data);
    } catch (err) {
      console.error('Failed to fetch donors', err);
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
      setPredicting(true);
      const response = await itemsAPI.predictCategory(formData.name);
      setPrediction(response.data);
      
      // Auto-select predicted category
      const predictedCat = categories.find(
        c => c.category_name === response.data.predicted_category
      );
      if (predictedCat) {
        setFormData({ ...formData, category_id: predictedCat.category_id });
      }
    } catch (err) {
      console.error('Prediction failed', err);
    } finally {
      setPredicting(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      const data = {
        ...formData,
        quantity: parseInt(formData.quantity),
        category_id: parseInt(formData.category_id),
        donor_id: parseInt(formData.donor_id),
      };

      await itemsAPI.create(data);
      alert('Item added successfully!');
      
      // Reset form
      setFormData({
        name: '',
        quantity: '',
        expiry_date: '',
        description: '',
        storage_condition: '',
        category_id: '',
        donor_id: '',
      });
      setPrediction(null);
    } catch (err) {
      alert('Failed to add item: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="add-item">
      <h1>➕ Add New Item</h1>

      <form onSubmit={handleSubmit} className="item-form">
        <div className="form-group">
          <label>Item Name *</label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
            placeholder="Enter item name"
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Quantity *</label>
            <input
              type="number"
              name="quantity"
              value={formData.quantity}
              onChange={handleChange}
              required
              min="0"
              placeholder="0"
            />
          </div>

          <div className="form-group">
            <label>Expiry Date *</label>
            <input
              type="date"
              name="expiry_date"
              value={formData.expiry_date}
              onChange={handleChange}
              required
              min={new Date().toISOString().split('T')[0]}
            />
          </div>
        </div>

        <div className="form-group">
          <label>Description</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows="3"
            placeholder="Optional: add details"
          />
          <button
            type="button"
            onClick={handlePredictCategory}
            disabled={predicting || !formData.name}
            className="btn-predict"
          >
            {predicting ? '🤖 Predicting...' : '🤖 Predict Category (using name)'}
          </button>
          
          {prediction && (
            <div className="prediction-result">
              <strong>Predicted:</strong> {prediction.predicted_category} 
              (Confidence: {(prediction.confidence * 100).toFixed(0)}%)
            </div>
          )}
        </div>

        <div className="form-group">
          <label>Storage Condition</label>
          <input
            type="text"
            name="storage_condition"
            value={formData.storage_condition}
            onChange={handleChange}
            placeholder="e.g., Cool and dry place, Refrigerated"
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Category *</label>
            <select
              name="category_id"
              value={formData.category_id}
              onChange={handleChange}
              required
            >
              <option value="">Select Category</option>
              {categories.map(cat => (
                <option key={cat.category_id} value={cat.category_id}>
                  {cat.category_name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Donor *</label>
            <select
              name="donor_id"
              value={formData.donor_id}
              onChange={handleChange}
              required
            >
              <option value="">Select Donor</option>
              {donors.map(donor => (
                <option key={donor.donor_id} value={donor.donor_id}>
                  {donor.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button type="submit" disabled={loading} className="btn-submit">
          {loading ? 'Adding...' : '✓ Add Item'}
        </button>
      </form>
    </div>
  );
}

export default AddItem;
