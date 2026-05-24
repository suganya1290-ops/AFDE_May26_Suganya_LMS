-- Library Management System
-- Phase 1 Database Schema
-- Compatible with SQLite and PostgreSQL

CREATE TABLE IF NOT EXISTS books (
    book_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title            TEXT NOT NULL,
    author           TEXT NOT NULL,
    category         TEXT NOT NULL,
    isbn             TEXT UNIQUE NOT NULL,
    availability_status TEXT DEFAULT 'available' CHECK(availability_status IN ('available', 'borrowed'))
);

CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_books_author ON books(author);
CREATE INDEX idx_books_category ON books(category);
CREATE INDEX idx_books_isbn ON books(isbn);

CREATE TABLE IF NOT EXISTS borrowers (
    borrower_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    borrower_name TEXT NOT NULL,
    email         TEXT UNIQUE NOT NULL,
    phone         TEXT NOT NULL
);

CREATE INDEX idx_borrowers_email ON borrowers(email);
CREATE INDEX idx_borrowers_name ON borrowers(borrower_name);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id        INTEGER NOT NULL REFERENCES books(book_id),
    borrower_id    INTEGER NOT NULL REFERENCES borrowers(borrower_id),
    borrow_date    DATETIME DEFAULT CURRENT_TIMESTAMP,
    return_date    DATETIME
);

CREATE INDEX idx_transactions_book ON transactions(book_id);
CREATE INDEX idx_transactions_borrower ON transactions(borrower_id);
CREATE INDEX idx_transactions_borrow_date ON transactions(borrow_date);

-- Sample Data
INSERT INTO books (title, author, category, isbn, availability_status) VALUES
  ('Clean Code', 'Robert C. Martin', 'Programming', '9780132350884', 'available'),
  ('The Pragmatic Programmer', 'Andrew Hunt', 'Programming', '9780201616224', 'available'),
  ('Designing Data-Intensive Applications', 'Martin Kleppmann', 'Data Engineering', '9781449373320', 'available'),
  ('Python Crash Course', 'Eric Matthes', 'Programming', '9781593279288', 'available'),
  ('Introduction to Algorithms', 'CLRS', 'Computer Science', '9780262033848', 'available');

INSERT INTO borrowers (borrower_name, email, phone) VALUES
  ('Rahul Sharma', 'rahul.sharma@example.com', '9876543210'),
  ('Ananya Gupta', 'ananya.gupta@example.com', '9876543211'),
  ('Karthik Nair', 'karthik.nair@example.com', '9876543212');
