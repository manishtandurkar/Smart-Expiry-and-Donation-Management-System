import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import DonorDashboard from './components/DonorDashboard';
import ReceiverDashboard from './components/ReceiverDashboard';
import AdminDashboard from './components/AdminDashboard';
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Clear any existing session on app start - always require fresh login
    localStorage.removeItem('user');
    localStorage.removeItem('userRole');
    setLoading(false);
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('user');
    localStorage.removeItem('userRole');
    setUser(null);
  };

  if (loading) {
    return (
      <div className="app-loading">
        <div className="loading-spinner">Loading...</div>
      </div>
    );
  }

  // If not logged in, show login screen
  if (!user) {
    return <Login onLogin={handleLogin} />;
  }

  // Render dashboard based on user role
  const renderDashboard = () => {
    switch (user.user.role) {
      case 'donor':
        return (
          <DonorDashboard 
            user={user.user} 
            donorId={user.donor_id}
            onLogout={handleLogout} 
          />
        );
      case 'receiver':
        return (
          <ReceiverDashboard 
            user={user.user} 
            receiverId={user.receiver_id}
            onLogout={handleLogout} 
          />
        );
      case 'admin':
        return (
          <AdminDashboard 
            user={user.user} 
            onLogout={handleLogout} 
          />
        );
      default:
        return <Login onLogin={handleLogin} />;
    }
  };

  return (
    <div className="app">
      {renderDashboard()}
    </div>
  );
}

export default App;
