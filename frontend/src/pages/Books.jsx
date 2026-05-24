import React, { useEffect, useState } from 'react';
import { booksAPI } from '../services/api';

const emptyForm = { title: '', author: '', category: '', isbn: '', availability_status: 'available' };

export default function Books() {
  const [books, setBooks] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [errors, setErrors] = useState({});
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const loadBooks = async () => {
    try {
      const response = await booksAPI.getAll();
      setBooks(response.data);
    } catch (err) {
      console.error(err);
      setMessage('Failed to load books');
    }
  };

  useEffect(() => {
    loadBooks();
  }, []);

  const validateForm = () => {
    const newErrors = {};
    if (!form.title.trim()) newErrors.title = 'Title is required';
    if (!form.author.trim()) newErrors.author = 'Author is required';
    if (!form.category.trim()) newErrors.category = 'Category is required';
    if (!form.isbn.trim()) newErrors.isbn = 'ISBN is required';
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
        await booksAPI.update(editingId, form);
        setMessage('✅ Book updated successfully');
      } else {
        await booksAPI.create(form);
        setMessage('✅ Book added successfully');
      }
      setForm(emptyForm);
      setEditingId(null);
      setShowForm(false);
      setErrors({});
      loadBooks();
    } catch (err) {
      setMessage(err.response?.data?.detail || '❌ Operation failed');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (book) => {
    setForm({ ...book });
    setEditingId(book.book_id);
    setShowForm(true);
    setErrors({});
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this book?')) {
      try {
        await booksAPI.delete(id);
        setMessage('✅ Book deleted');
        loadBooks();
      } catch (err) {
        setMessage('❌ Failed to delete book');
      }
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">📚 Book Management</h1>
        <button
          className="btn btn-primary"
          onClick={() => {
            setShowForm(!showForm);
            setForm(emptyForm);
            setEditingId(null);
            setErrors({});
          }}
        >
          {showForm ? '✕ Cancel' : '+ Add Book'}
        </button>
      </div>

      {message && <div className="message">{message}</div>}

      {showForm && (
        <form className="form-card" onSubmit={handleSubmit}>
          <h2>{editingId ? 'Edit Book' : 'Add New Book'}</h2>
          <div className="form-grid">
            {['title', 'author', 'category', 'isbn'].map((field) => (
              <div className="form-group" key={field}>
                <label>{field.charAt(0).toUpperCase() + field.slice(1)}</label>
                <input
                  className={`form-input ${errors[field] ? 'error' : ''}`}
                  value={form[field]}
                  onChange={(e) => setForm({ ...form, [field]: e.target.value })}
                  placeholder={`Enter ${field}`}
                />
                {errors[field] && <span className="error-text">{errors[field]}</span>}
              </div>
            ))}
            <div className="form-group">
              <label>Availability</label>
              <select
                className="form-input"
                value={form.availability_status}
                onChange={(e) => setForm({ ...form, availability_status: e.target.value })}
              >
                <option value="available">Available</option>
                <option value="borrowed">Borrowed</option>
              </select>
            </div>
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Processing...' : editingId ? 'Update Book' : 'Add Book'}
          </button>
        </form>
      )}

      <div className="table-container">
        {books.length === 0 ? (
          <div className="empty-state">No books in the library yet. Add one!</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Author</th>
                <th>Category</th>
                <th>ISBN</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {books.map((book) => (
                <tr key={book.book_id}>
                  <td>{book.book_id}</td>
                  <td>{book.title}</td>
                  <td>{book.author}</td>
                  <td>{book.category}</td>
                  <td>{book.isbn}</td>
                  <td>
                    <span className={`badge badge-${book.availability_status}`}>
                      {book.availability_status}
                    </span>
                  </td>
                  <td>
                    <button className="btn btn-sm" onClick={() => handleEdit(book)}>
                      Edit
                    </button>
                    <button
                      className="btn btn-sm btn-danger"
                      onClick={() => handleDelete(book.book_id)}
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
