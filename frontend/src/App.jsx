import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import AddItem from './components/AddItem';
import Inventory from './components/Inventory';
import Alerts from './components/Alerts';
import RecordDonation from './components/RecordDonation';
import Donations from './components/Donations';
import Admin from './components/Admin';
import './App.css';

function App() {
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    setIsAdmin(Boolean(localStorage.getItem('isAdmin')));
    function onAdminChange() {
      setIsAdmin(Boolean(localStorage.getItem('isAdmin')));
    }
    window.addEventListener('admin-change', onAdminChange);
    return () => window.removeEventListener('admin-change', onAdminChange);
  }, []);

  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <div className="nav-brand">
            <h2>🔄 Smart Expiry & Donation System</h2>
            <p className="nav-subtitle"></p>
          </div>
          {isAdmin ? (
            <a className="admin-login-button" onClick={() => { localStorage.removeItem('isAdmin'); window.dispatchEvent(new Event('admin-change')); window.location.href = '/'; }}>Logout</a>
          ) : (
            <NavLink to="/admin" className={({ isActive }) => isActive ? 'admin-login-button active' : 'admin-login-button'}>Admin Login</NavLink>
          )}
          {!isAdmin && (
            <div className="nav-links">
            <NavLink to="/" end className={({ isActive }) => isActive ? 'active' : ''}>Dashboard</NavLink>
            <NavLink to="/add-item" className={({ isActive }) => isActive ? 'active' : ''}>Add Item</NavLink>
            <NavLink to="/inventory" className={({ isActive }) => isActive ? 'active' : ''}>Inventory</NavLink>
            <NavLink to="/alerts" className={({ isActive }) => isActive ? 'active' : ''}>Alerts</NavLink>
            <NavLink to="/record-donation" className={({ isActive }) => isActive ? 'active' : ''}>Record Donation</NavLink>
            <NavLink to="/donations" className={({ isActive }) => isActive ? 'active' : ''}>Donations</NavLink>
            </div>
          )}
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/add-item" element={<AddItem />} />
            <Route path="/inventory" element={<Inventory />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/record-donation" element={<RecordDonation />} />
            <Route path="/donations" element={<Donations />} />
            <Route path="/admin" element={<Admin />} />
          </Routes>
        </main>

        {/* footer removed per request */}
      </div>
    </Router>
  );
}

export default App;
