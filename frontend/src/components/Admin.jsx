import React, { useEffect, useState } from 'react';
import { donorsAPI, receiversAPI, adminAPI } from '../services/api';
import { useNavigate } from 'react-router-dom';

export default function Admin() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [authed, setAuthed] = useState(false);
  const [adminPassword, setAdminPassword] = useState('');

  const [donors, setDonors] = useState([]);
  const [receivers, setReceivers] = useState([]);

  const [newDonor, setNewDonor] = useState({ name: '', contact: '', address: '' });
  const [newReceiver, setNewReceiver] = useState({ name: '', contact: '', address: '', organization_type: '' });

  useEffect(() => {
    if (authed) {
      fetchLists();
    }
  }, [authed]);

  useEffect(() => {
    // if stored as admin, set authed
    const stored = localStorage.getItem('isAdmin');
    if (stored) setAuthed(true);
    const storedPass = localStorage.getItem('adminPassword');
    if (storedPass) setAdminPassword(storedPass);
  }, []);

  async function fetchLists() {
    try {
      const d = await donorsAPI.getAll();
      setDonors(d.data || []);
      const r = await receiversAPI.getAll();
      setReceivers(r.data || []);
    } catch (err) {
      console.error(err);
    }
  }

  async function handleLogin(e) {
    e.preventDefault();
    try {
      await adminAPI.login(username, password);
      setAuthed(true);
      setAdminPassword(password);
      localStorage.setItem('isAdmin', '1');
      localStorage.setItem('adminPassword', password);
      window.dispatchEvent(new Event('admin-change'));
      setPassword('');
      setUsername('');
    } catch (err) {
      alert('Invalid credentials');
    }
  }

  const navigate = useNavigate();

  function handleLogout() {
    localStorage.removeItem('isAdmin');
    localStorage.removeItem('adminPassword');
    window.dispatchEvent(new Event('admin-change'));
    setAuthed(false);
    setAdminPassword('');
    navigate('/');
  }

  async function handleCreateDonor(e) {
    e.preventDefault();
    try {
      await donorsAPI.create(newDonor);
      setNewDonor({ name: '', contact: '', address: '' });
      fetchLists();
    } catch (err) {
      alert(err.response?.data?.detail || err.message);
    }
  }

  async function handleCreateReceiver(e) {
    e.preventDefault();
    try {
      await receiversAPI.create(newReceiver);
      setNewReceiver({ name: '', contact: '', address: '', organization_type: '' });
      fetchLists();
    } catch (err) {
      alert(err.response?.data?.detail || err.message);
    }
  }

  const [confirmState, setConfirmState] = useState(null);

  async function handleDeleteDonor(id, name) {
    if (!localStorage.getItem('isAdmin')) return alert('Please login as admin first');
    setConfirmState({ type: 'donor', id, name });
  }

  async function handleDeleteReceiver(id, name) {
    if (!localStorage.getItem('isAdmin')) return alert('Please login as admin first');
    setConfirmState({ type: 'receiver', id, name });
  }

  if (!authed) {
    return (
      <div className="admin-login card">
        <h3>Admin Login</h3>
        <p style={{ color: '#475569', marginBottom: 12 }}>Enter admin credentials to manage donors and receivers.</p>
        <form onSubmit={handleLogin}>
          <div className="form-group">
            <label>Username</label>
            <input value={username} onChange={e => setUsername(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required />
          </div>
          <button type="submit" className="btn-submit">Login</button>
        </form>
      </div>
    );
  }

  return (
    <div className="admin-screen">
      <h2>Admin Console</h2>

      <section className="admin-section card">
        <h3>Donors</h3>
        <form onSubmit={handleCreateDonor} className="inline-form">
          <input placeholder="Name" value={newDonor.name} onChange={e => setNewDonor({ ...newDonor, name: e.target.value })} required />
          <input placeholder="Contact (digits)" value={newDonor.contact} onChange={e => setNewDonor({ ...newDonor, contact: e.target.value })} required />
          <input placeholder="Address" value={newDonor.address} onChange={e => setNewDonor({ ...newDonor, address: e.target.value })} />
          <button type="submit">Add Donor</button>
        </form>

        <table className="admin-table">
          <thead>
            <tr>
              <th>Name</th>
              <th className="col-contact">Contact</th>
              <th>Address</th>
              <th className="col-actions">Actions</th>
            </tr>
          </thead>
          <tbody>
            {donors.map(d => (
              <tr key={d.donor_id}>
                <td>{d.name}</td>
                <td className="col-contact">{d.contact}</td>
                <td>{d.address || ''}</td>
                <td className="col-actions"><button className="danger" onClick={() => handleDeleteDonor(d.donor_id, d.name)}>Delete</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="admin-section card">
        <h3>Receivers</h3>
        <form onSubmit={handleCreateReceiver} className="inline-form">
          <input placeholder="Name" value={newReceiver.name} onChange={e => setNewReceiver({ ...newReceiver, name: e.target.value })} required />
          <input placeholder="Contact (digits)" value={newReceiver.contact} onChange={e => setNewReceiver({ ...newReceiver, contact: e.target.value })} required />
          <input placeholder="Organization" value={newReceiver.organization_type} onChange={e => setNewReceiver({ ...newReceiver, organization_type: e.target.value })} />
          <input placeholder="Address" value={newReceiver.address} onChange={e => setNewReceiver({ ...newReceiver, address: e.target.value })} />
          <button type="submit">Add Receiver</button>
        </form>

        <table className="admin-table">
          <thead>
            <tr>
              <th>Name</th>
              <th className="col-contact">Contact</th>
              <th>Organization</th>
              <th>Address</th>
              <th className="col-actions">Actions</th>
            </tr>
          </thead>
          <tbody>
            {receivers.map(r => (
              <tr key={r.receiver_id}>
                <td>{r.name}</td>
                <td className="col-contact">{r.contact}</td>
                <td>{r.organization_type || ''}</td>
                <td>{r.address || ''}</td>
                <td className="col-actions"><button className="danger" onClick={() => handleDeleteReceiver(r.receiver_id, r.name)}>Delete</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
      {/* Confirmation modal */}
      {confirmState && (
        <div className="modal-backdrop">
          <div className="modal-card">
            <h4>Confirm delete</h4>
            <p>Are you sure you want to delete the {confirmState.type} "{confirmState.name}"?</p>
            <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end', marginTop: 12 }}>
              <button onClick={() => setConfirmState(null)} className="btn">Cancel</button>
              <button
                className="danger"
                onClick={async () => {
                  try {
                    const pwd = localStorage.getItem('adminPassword') || adminPassword;
                    if (!pwd) return alert('Admin password not available; please re-login');
                    if (confirmState.type === 'donor') {
                      await donorsAPI.delete(confirmState.id, pwd);
                    } else {
                      await receiversAPI.delete(confirmState.id, pwd);
                    }
                    setConfirmState(null);
                    fetchLists();
                  } catch (err) {
                    alert(err.response?.data?.detail || err.message);
                  }
                }}
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
