import React, { useEffect, useState } from 'react';
import { dashboardAPI } from '../services/api';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await dashboardAPI.getStats();
        setStats(response.data);
      } catch (err) {
        setError('Failed to load dashboard statistics');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return <div className="page"><p className="loading">Loading dashboard...</p></div>;
  }

  if (error) {
    return <div className="page"><p className="error">{error}</p></div>;
  }

  const statCards = [
    { label: 'Total Books', value: stats.total_books, icon: '📚', color: '#4f8ef7' },
    { label: 'Available', value: stats.available_books, icon: '✅', color: '#34c97b' },
    { label: 'Borrowed', value: stats.borrowed_books, icon: '📖', color: '#f7a94f' },
    { label: 'Total Borrowers', value: stats.total_borrowers, icon: '👥', color: '#b16ef7' },
    { label: 'Total Transactions', value: stats.total_transactions, icon: '🔄', color: '#f76e6e' },
    { label: 'Active Loans', value: stats.active_transactions, icon: '⏳', color: '#4fc7f7' },
  ];

  return (
    <div className="page">
      <h1 className="page-title">📊 Dashboard</h1>

      <div className="stats-grid">
        {statCards.map((card) => (
          <div className="stat-card" key={card.label} style={{ borderTop: `4px solid ${card.color}` }}>
            <span className="stat-icon">{card.icon}</span>
            <div className="stat-value" style={{ color: card.color }}>
              {card.value}
            </div>
            <div className="stat-label">{card.label}</div>
          </div>
        ))}
      </div>

      <h2 className="section-title">Recent Transactions</h2>
      {stats.recent_transactions.length === 0 ? (
        <div className="empty-state">No transactions yet</div>
      ) : (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>#ID</th>
                <th>Book</th>
                <th>Borrower</th>
                <th>Borrowed</th>
                <th>Returned</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {stats.recent_transactions.map((tx) => (
                <tr key={tx.transaction_id}>
                  <td>{tx.transaction_id}</td>
                  <td>{tx.book_title}</td>
                  <td>{tx.borrower_name}</td>
                  <td>{new Date(tx.borrow_date).toLocaleDateString()}</td>
                  <td>{tx.return_date ? new Date(tx.return_date).toLocaleDateString() : '—'}</td>
                  <td>
                    <span className={`badge badge-${tx.status}`}>{tx.status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
