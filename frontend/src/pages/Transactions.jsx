import React, { useEffect, useState } from 'react';
import { booksAPI, borrowersAPI, transactionsAPI } from '../services/api';

export default function Transactions() {
  const [books, setBooks] = useState([]);
  const [borrowers, setBorrowers] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [borrowForm, setBorrowForm] = useState({ book_id: '', borrower_id: '' });
  const [returnForm, setReturnForm] = useState({ book_id: '', borrower_id: '' });
  const [message, setMessage] = useState('');
  const [activeTab, setActiveTab] = useState('borrow');
  const [loading, setLoading] = useState(false);

  const loadData = async () => {
    try {
      const [booksRes, borrowersRes, transRes] = await Promise.all([
        booksAPI.getAll(),
        borrowersAPI.getAll(),
        transactionsAPI.getAll(),
      ]);
      setBooks(booksRes.data);
      setBorrowers(borrowersRes.data);
      setTransactions(transRes.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const showMessage = (msg) => {
    setMessage(msg);
    setTimeout(() => setMessage(''), 3000);
  };

  const handleBorrow = async (e) => {
    e.preventDefault();
    if (!borrowForm.book_id || !borrowForm.borrower_id) {
      showMessage('❌ Please select both book and borrower');
      return;
    }
    setLoading(true);
    try {
      await transactionsAPI.borrow(parseInt(borrowForm.book_id), parseInt(borrowForm.borrower_id));
      showMessage('✅ Book borrowed successfully');
      setBorrowForm({ book_id: '', borrower_id: '' });
      loadData();
    } catch (err) {
      showMessage('❌ ' + (err.response?.data?.detail || 'Failed to borrow book'));
    } finally {
      setLoading(false);
    }
  };

  const handleReturn = async (e) => {
    e.preventDefault();
    if (!returnForm.book_id || !returnForm.borrower_id) {
      showMessage('❌ Please select both book and borrower');
      return;
    }
    setLoading(true);
    try {
      await transactionsAPI.return(parseInt(returnForm.book_id), parseInt(returnForm.borrower_id));
      showMessage('✅ Book returned successfully');
      setReturnForm({ book_id: '', borrower_id: '' });
      loadData();
    } catch (err) {
      showMessage('❌ ' + (err.response?.data?.detail || 'Failed to return book'));
    } finally {
      setLoading(false);
    }
  };

  const availableBooks = books.filter((b) => b.availability_status === 'available');
  const borrowedBooks = books.filter((b) => b.availability_status === 'borrowed');

  return (
    <div className="page">
      <h1 className="page-title">🔄 Borrow & Return</h1>
      {message && <div className="message">{message}</div>}

      <div className="tabs">
        <button className={`tab ${activeTab === 'borrow' ? 'active' : ''}`} onClick={() => setActiveTab('borrow')}>
          📤 Borrow Book
        </button>
        <button className={`tab ${activeTab === 'return' ? 'active' : ''}`} onClick={() => setActiveTab('return')}>
          📥 Return Book
        </button>
        <button className={`tab ${activeTab === 'history' ? 'active' : ''}`} onClick={() => setActiveTab('history')}>
          📋 History
        </button>
      </div>

      {activeTab === 'borrow' && (
        <form className="form-card" onSubmit={handleBorrow}>
          <h2>Borrow a Book</h2>
          <div className="form-grid">
            <div className="form-group">
              <label>Select Available Book</label>
              <select
                className="form-input"
                value={borrowForm.book_id}
                onChange={(e) => setBorrowForm({ ...borrowForm, book_id: e.target.value })}
              >
                <option value="">-- Choose a book --</option>
                {availableBooks.map((b) => (
                  <option key={b.book_id} value={b.book_id}>
                    {b.title} — {b.author}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Select Borrower</label>
              <select
                className="form-input"
                value={borrowForm.borrower_id}
                onChange={(e) => setBorrowForm({ ...borrowForm, borrower_id: e.target.value })}
              >
                <option value="">-- Choose a borrower --</option>
                {borrowers.map((b) => (
                  <option key={b.borrower_id} value={b.borrower_id}>
                    {b.borrower_name} ({b.email})
                  </option>
                ))}
              </select>
            </div>
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Processing...' : 'Borrow Book'}
          </button>
        </form>
      )}

      {activeTab === 'return' && (
        <form className="form-card" onSubmit={handleReturn}>
          <h2>Return a Book</h2>
          <div className="form-grid">
            <div className="form-group">
              <label>Select Borrowed Book</label>
              <select
                className="form-input"
                value={returnForm.book_id}
                onChange={(e) => setReturnForm({ ...returnForm, book_id: e.target.value })}
              >
                <option value="">-- Choose a book --</option>
                {borrowedBooks.map((b) => (
                  <option key={b.book_id} value={b.book_id}>
                    {b.title} — {b.author}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Select Borrower</label>
              <select
                className="form-input"
                value={returnForm.borrower_id}
                onChange={(e) => setReturnForm({ ...returnForm, borrower_id: e.target.value })}
              >
                <option value="">-- Choose a borrower --</option>
                {borrowers.map((b) => (
                  <option key={b.borrower_id} value={b.borrower_id}>
                    {b.borrower_name} ({b.email})
                  </option>
                ))}
              </select>
            </div>
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Processing...' : 'Return Book'}
          </button>
        </form>
      )}

      {activeTab === 'history' && (
        <div className="table-container">
          {transactions.length === 0 ? (
            <div className="empty-state">No transactions yet</div>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Book Title</th>
                  <th>Borrower Name</th>
                  <th>Borrow Date</th>
                  <th>Return Date</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {[...transactions].reverse().map((tx) => (
                  <tr key={tx.transaction_id}>
                    <td>{tx.transaction_id}</td>
                    <td>{tx.book ? tx.book.title : `Book #${tx.book_id}`}</td>
                    <td>{tx.borrower ? tx.borrower.borrower_name : `Borrower #${tx.borrower_id}`}</td>
                    <td>{new Date(tx.borrow_date).toLocaleDateString()}</td>
                    <td>{tx.return_date ? new Date(tx.return_date).toLocaleDateString() : '—'}</td>
                    <td>
                      <span className={`badge badge-${tx.return_date ? 'returned' : 'active'}`}>
                        {tx.return_date ? 'Returned' : 'Active'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}
