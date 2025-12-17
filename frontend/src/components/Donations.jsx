import React, { useState, useEffect } from 'react';
import { donationsAPI } from '../services/api';
import './Donations.css';

function Donations() {
  const [donations, setDonations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDonations();
  }, []);

  const fetchDonations = async () => {
    try {
      const response = await donationsAPI.getAll();
      setDonations(response.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading donations...</div>;

  return (
    <div className="donations">
      <h1>📋 Donation History ({donations.length} records)</h1>
      
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Date</th>
              <th>Item</th>
              <th>Category</th>
              <th>Quantity</th>
              <th>Receiver</th>
              <th>Organization</th>
              <th>Notes</th>
            </tr>
          </thead>
          <tbody>
            {donations.map(donation => (
              <tr key={donation.donation_id}>
                <td>{donation.donation_id}</td>
                <td>
                  {new Date(donation.created_at).toLocaleDateString()}<br/>
                  <small style={{color: '#64748b'}}>{new Date(donation.created_at).toLocaleTimeString()}</small>
                </td>
                <td><strong>{donation.item.name}</strong></td>
                <td>{donation.item.category_name}</td>
                <td>{donation.quantity}</td>
                <td>{donation.receiver.name}</td>
                <td>{donation.receiver.organization_type || '-'}</td>
                <td>{donation.notes || '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Donations;
