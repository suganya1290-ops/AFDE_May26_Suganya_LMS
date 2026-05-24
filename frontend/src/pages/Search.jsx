import React, { useState } from 'react';
import { searchAPI } from '../services/api';

export default function Search() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [searched, setSearched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState('all');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      const response = await searchAPI.books(query);
      setResults(response.data);
      setSearched(true);
    } catch (err) {
      console.error(err);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const filtered = filter === 'all' ? results : results.filter((b) => b.availability_status === filter);

  return (
    <div className="page">
      <h1 className="page-title">🔍 Search Books</h1>

      <form onSubmit={handleSearch} className="search-form">
        <input
          className="search-input"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by title, author, category, or ISBN..."
        />
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {searched && (
        <>
          <div className="filter-controls">
            <span>Filter:</span>
            {['all', 'available', 'borrowed'].map((f) => (
              <button
                key={f}
                className={`filter-btn ${filter === f ? 'active' : ''}`}
                onClick={() => setFilter(f)}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>

          <p className="result-count">{filtered.length} result{filtered.length !== 1 ? 's' : ''} found</p>

          {filtered.length === 0 ? (
            <div className="empty-state">No books matched your search.</div>
          ) : (
            <div className="books-grid">
              {filtered.map((book) => (
                <div className="book-card" key={book.book_id}>
                  <div className="book-header">
                    <span className="book-category">{book.category}</span>
                    <span className={`badge badge-${book.availability_status}`}>
                      {book.availability_status}
                    </span>
                  </div>
                  <h3 className="book-title">{book.title}</h3>
                  <p className="book-author">by {book.author}</p>
                  <p className="book-isbn">ISBN: {book.isbn}</p>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {!searched && (
        <div className="search-hint">
          <p>📚</p>
          <p>Enter a keyword to search the library catalog.</p>
        </div>
      )}
    </div>
  );
}
