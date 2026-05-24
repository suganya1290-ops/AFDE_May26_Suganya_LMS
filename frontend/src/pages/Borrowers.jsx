import React, { useEffect, useState } from 'react';
import { borrowersAPI } from '../services/api';

const emptyForm = { borrower_name: '', email: '', phone: '' };

export default function Borrowers() {
  const [borrowers, setBorrowers] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [errors, setErrors] = useState({});
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const loadBorrowers = async () => {
    try {
      const response = await borrowersAPI.getAll();
      setBorrowers(response.data);
    } catch (err) {
      console.error(err);
      setMessage('Failed to load borrowers');
      setBorrowers([]);
    }
  };

  useEffect(() => {
    loadBorrowers();
  }, []);

  const validateForm = () => {
    const newErrors = {};
    if (!form.borrower_name.trim()) newErrors.borrower_name = 'Name is required';
    if (!form.email.match(/\S+@\S+\.\S+/)) newErrors.email = 'Valid email is required';
    if (!form.phone.trim()) newErrors.phone = 'Phone is required';
    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formErrors = validateForm();
    if (Object.keys(formErrors).length > 0) {
      setErrors(formErrors);
      return;
    }

    setLoading(true);
    try {
      if (editingId) {
        await borrowersAPI.update(editingId, form);
        setMessage('✅ Borrower updated successfully');
      } else {
        await borrowersAPI.create(form);
        setMessage('✅ Borrower added successfully');
      }
      setForm(emptyForm);
      setEditingId(null);
      setShowForm(false);
      setErrors({});
      loadBorrowers();
    } catch (err) {
      setMessage(err.response?.data?.detail || '❌ Operation failed');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (borrower) => {
    setForm({ ...borrower });
    setEditingId(borrower.borrower_id);
    setShowForm(true);
    setErrors({});
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this borrower?')) {
      try {
        await borrowersAPI.delete(id);
        setMessage('✅ Borrower deleted');
        loadBorrowers();
      } catch (err) {
        setMessage('❌ Failed to delete borrower');
      }
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">👥 Borrower Management</h1>
        <button
          className="btn btn-primary"
          onClick={() => {
            setShowForm(!showForm);
            setForm(emptyForm);
            setEditingId(null);
            setErrors({});
          }}
        >
          {showForm ? '✕ Cancel' : '+ Add Borrower'}
        </button>
      </div>

      {message && (
        <div className="message" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>{message}</span>
          {message.includes('Failed') && (
            <button className="btn btn-primary btn-sm" onClick={loadBorrowers}>Retry</button>
          )}
        </div>
      )}

      {showForm && (
        <form className="form-card" onSubmit={handleSubmit}>
          <h2>{editingId ? 'Edit Borrower' : 'Register New Borrower'}</h2>
          <div className="form-grid">
            <div className="form-group">
              <label>Full Name</label>
              <input
                className={`form-input ${errors.borrower_name ? 'error' : ''}`}
                value={form.borrower_name}
                onChange={(e) => setForm({ ...form, borrower_name: e.target.value })}
                placeholder="Enter full name"
              />
              {errors.borrower_name && <span className="error-text">{errors.borrower_name}</span>}
            </div>
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                className={`form-input ${errors.email ? 'error' : ''}`}
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                placeholder="Enter email"
              />
              {errors.email && <span className="error-text">{errors.email}</span>}
            </div>
            <div className="form-group">
              <label>Phone</label>
              <input
                className={`form-input ${errors.phone ? 'error' : ''}`}
                value={form.phone}
                onChange={(e) => setForm({ ...form, phone: e.target.value })}
                placeholder="Enter phone number"
              />
              {errors.phone && <span className="error-text">{errors.phone}</span>}
            </div>
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Processing...' : editingId ? 'Update Borrower' : 'Add Borrower'}
          </button>
        </form>
      )}

      <div className="table-container">
        {borrowers.length === 0 ? (
          <div className="empty-state">No borrowers registered yet. Add one!</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {borrowers.map((borrower) => (
                <tr key={borrower.borrower_id}>
                  <td>{borrower.borrower_id}</td>
                  <td>{borrower.borrower_name}</td>
                  <td>{borrower.email}</td>
                  <td>{borrower.phone}</td>
                  <td>
                    <button className="btn btn-sm" onClick={() => handleEdit(borrower)}>
                      Edit
                    </button>
                    <button
                      className="btn btn-sm btn-danger"
                      onClick={() => handleDelete(borrower.borrower_id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
