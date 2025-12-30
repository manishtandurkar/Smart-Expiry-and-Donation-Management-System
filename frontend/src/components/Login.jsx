import React, { useState } from 'react';
import { authAPI } from '../services/api';
import './Login.css';

function Login({ onLogin }) {
  const [selectedRole, setSelectedRole] = useState(null);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleRoleSelect = (role) => {
    setSelectedRole(role);
    setError('');
    setUsername('');
    setPassword('');
  };

  const handleBack = () => {
    setSelectedRole(null);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await authAPI.login(username, password);
      const userData = response.data;

      // Verify role matches
      if (userData.user.role !== selectedRole) {
        setError(`This account is registered as ${userData.user.role}, not ${selectedRole}`);
        setLoading(false);
        return;
      }

      // Store user data in localStorage
      localStorage.setItem('user', JSON.stringify(userData));
      localStorage.setItem('userRole', userData.user.role);

      onLogin(userData);
    } catch (err) {
      let errorMsg = 'Invalid username or password';
      if (err.response?.data?.detail) {
        errorMsg = typeof err.response.data.detail === 'string'
          ? err.response.data.detail
          : JSON.stringify(err.response.data.detail);
      }
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const getRoleIcon = (role) => {
    switch (role) {
      case 'donor': return '🎁';
      case 'receiver': return '🏢';
      case 'admin': return '⚙️';
      default: return '👤';
    }
  };

  const getRoleDescription = (role) => {
    switch (role) {
      case 'donor': return 'Add items you want to donate to the common inventory';
      case 'receiver': return 'Request items from inventory for your organization';
      case 'admin': return 'Manage users and approve donation requests';
      default: return '';
    }
  };

  if (!selectedRole) {
    return (
      <div className="login-container">
        <div className="login-header">
          <h1>🔄 Smart Expiry & Donation System</h1>
          <p>Select your role to continue</p>
        </div>

        <div className="role-cards">
          <div className="role-card" onClick={() => handleRoleSelect('donor')}>
            <span className="role-icon">{getRoleIcon('donor')}</span>
            <h2>Donor</h2>
            <p>{getRoleDescription('donor')}</p>
            <button className="role-btn donor-btn">Login as Donor</button>
          </div>

          <div className="role-card" onClick={() => handleRoleSelect('receiver')}>
            <span className="role-icon">{getRoleIcon('receiver')}</span>
            <h2>Receiver</h2>
            <p>{getRoleDescription('receiver')}</p>
            <button className="role-btn receiver-btn">Login as Receiver</button>
          </div>

          <div className="role-card" onClick={() => handleRoleSelect('admin')}>
            <span className="role-icon">{getRoleIcon('admin')}</span>
            <h2>Admin</h2>
            <p>{getRoleDescription('admin')}</p>
            <button className="role-btn admin-btn">Login as Admin</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="login-container">
      <div className="login-box">
        <button className="back-btn" onClick={handleBack}>← Back</button>

        <div className="login-header">
          <span className="role-icon-large">{getRoleIcon(selectedRole)}</span>
          <h2>{selectedRole.charAt(0).toUpperCase() + selectedRole.slice(1)} Login</h2>
          <p>{getRoleDescription(selectedRole)}</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {error && <div className="error-message">{error}</div>}

          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              required
              autoFocus
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
            />
          </div>

          <button type="submit" className={`submit-btn ${selectedRole}-btn`} disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div className="demo-credentials">
          <p>Demo credentials (username = password):</p>
          {selectedRole === 'donor' && (
            <div>
              <code>greenvalleyfarm / greenvalleyfarm</code><br />
              <code>citymedicalstore / citymedicalstore</code><br />
              <code>fashionhub / fashionhub</code><br />
              <code>communitycenter / communitycenter</code>
            </div>
          )}
          {selectedRole === 'receiver' && (
            <div>
              <code>hopeorphanage / hopeorphanage</code><br />
              <code>seniorcitizensh / seniorcitizensh</code><br />
              <code>disasterrelief / disasterrelief</code><br />
              <code>homelessshelter / homelessshelter</code>
            </div>
          )}
          {selectedRole === 'admin' && <code>admin / admin</code>}
        </div>
      </div>
    </div>
  );
}

export default Login;
