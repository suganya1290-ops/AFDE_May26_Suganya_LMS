# Library Management System - API Documentation

**Base URL**: `http://localhost:8000`

**API Version**: 1.0.0

---

## Authentication

Currently Phase 1 does NOT require authentication.

---

## Response Format

All responses are in JSON format with consistent structure.

### Success Response
```json
{
  "data": {...},
  "status": "success",
  "timestamp": "2024-01-26T10:30:00"
}
```

### Error Response
```json
{
  "detail": "Error message describing what went wrong",
  "status": "error",
  "timestamp": "2024-01-26T10:30:00"
}
```

---

## Endpoints

### BOOKS MANAGEMENT

---

#### GET /books/

Get all books in the library.

**Query Parameters:**
- `skip` (int, optional): Skip N records (default: 0)
- `limit` (int, optional): Return N records (default: 100)

**Example Request:**
```bash
curl -X GET "http://localhost:8000/books/?skip=0&limit=10"
```

**Response:** `200 OK`
```json
[
  {
    "book_id": 1,
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "category": "Programming",
    "isbn": "9780132350884",
    "availability_status": "available"
  },
  {
    "book_id": 2,
    "title": "Python Crash Course",
    "author": "Eric Matthes",
    "category": "Programming",
    "isbn": "9781593279288",
    "availability_status": "borrowed"
  }
]
```

---

#### GET /books/{id}

Get a specific book by ID.

**Path Parameters:**
- `id` (int): Book ID

**Example Request:**
```bash
curl -X GET "http://localhost:8000/books/1"
```

**Response:** `200 OK`
```json
{
  "book_id": 1,
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "category": "Programming",
  "isbn": "9780132350884",
  "availability_status": "available"
}
```

**Error:** `404 Not Found`
```json
{
  "detail": "Book with ID 999 not found"
}
```

---

#### POST /books/

Create a new book.

**Request Body:**
```json
{
  "title": "The Pragmatic Programmer",
  "author": "Andrew Hunt",
  "category": "Programming",
  "isbn": "9780201616224",
  "availability_status": "available"
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/books/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Pragmatic Programmer",
    "author": "Andrew Hunt",
    "category": "Programming",
    "isbn": "9780201616224"
  }'
```

**Response:** `201 Created`
```json
{
  "book_id": 6,
  "title": "The Pragmatic Programmer",
  "author": "Andrew Hunt",
  "category": "Programming",
  "isbn": "9780201616224",
  "availability_status": "available"
}
```

**Error:** `400 Bad Request` (ISBN already exists)
```json
{
  "detail": "ISBN already exists in the system"
}
```

---

#### PUT /books/{id}

Update book details.

**Path Parameters:**
- `id` (int): Book ID

**Request Body:** (All fields optional)
```json
{
  "title": "The Pragmatic Programmer (Updated)",
  "availability_status": "borrowed"
}
```

**Example Request:**
```bash
curl -X PUT "http://localhost:8000/books/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Clean Code (2nd Edition)"
  }'
```

**Response:** `200 OK`
```json
{
  "book_id": 1,
  "title": "Clean Code (2nd Edition)",
  "author": "Robert C. Martin",
  "category": "Programming",
  "isbn": "9780132350884",
  "availability_status": "available"
}
```

---

#### DELETE /books/{id}

Delete a book.

**Path Parameters:**
- `id` (int): Book ID

**Example Request:**
```bash
curl -X DELETE "http://localhost:8000/books/1"
```

**Response:** `204 No Content`

**Error:** `404 Not Found`

---

### BORROWERS MANAGEMENT

---

#### GET /borrowers/

Get all borrowers.

**Query Parameters:**
- `skip` (int, optional): Skip N records (default: 0)
- `limit` (int, optional): Return N records (default: 100)

**Example Request:**
```bash
curl -X GET "http://localhost:8000/borrowers/?limit=5"
```

**Response:** `200 OK`
```json
[
  {
    "borrower_id": 1,
    "borrower_name": "Rahul Sharma",
    "email": "rahul.sharma@example.com",
    "phone": "9876543210"
  },
  {
    "borrower_id": 2,
    "borrower_name": "Ananya Gupta",
    "email": "ananya.gupta@example.com",
    "phone": "9876543211"
  }
]
```

---

#### POST /borrowers/

Register a new borrower.

**Request Body:**
```json
{
  "borrower_name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1-555-123-4567"
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/borrowers/" \
  -H "Content-Type: application/json" \
  -d '{
    "borrower_name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1-555-123-4567"
  }'
```

**Response:** `201 Created`
```json
{
  "borrower_id": 4,
  "borrower_name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1-555-123-4567"
}
```

**Error:** `400 Bad Request` (Email already registered)
```json
{
  "detail": "Email already registered in the system"
}
```

---

#### PUT /borrowers/{id}

Update borrower details.

**Path Parameters:**
- `id` (int): Borrower ID

**Request Body:** (All fields optional)
```json
{
  "email": "newemail@example.com",
  "phone": "9999999999"
}
```

---

#### DELETE /borrowers/{id}

Delete a borrower.

**Path Parameters:**
- `id` (int): Borrower ID

---

### TRANSACTIONS

---

#### POST /borrow

Record a book borrow transaction.

**Request Body:**
```json
{
  "book_id": 1,
  "borrower_id": 1
}
```

**Validation:**
- Book must exist and be "available"
- Borrower must exist
- Book status automatically changes to "borrowed"

**Example Request:**
```bash
curl -X POST "http://localhost:8000/borrow" \
  -H "Content-Type: application/json" \
  -d '{
    "book_id": 1,
    "borrower_id": 1
  }'
```

**Response:** `201 Created`
```json
{
  "transaction_id": 1,
  "book_id": 1,
  "borrower_id": 1,
  "borrow_date": "2024-01-26T10:30:00",
  "return_date": null,
  "book": {...},
  "borrower": {...}
}
```

**Error:** `400 Bad Request` (Book not available)
```json
{
  "detail": "Book is not available for borrowing"
}
```

---

#### POST /return

Record a book return transaction.

**Request Body:**
```json
{
  "book_id": 1,
  "borrower_id": 1
}
```

**Validation:**
- An active (non-returned) transaction must exist
- return_date is automatically set to current time
- Book status automatically changes to "available"

**Example Request:**
```bash
curl -X POST "http://localhost:8000/return" \
  -H "Content-Type: application/json" \
  -d '{
    "book_id": 1,
    "borrower_id": 1
  }'
```

**Response:** `200 OK`
```json
{
  "transaction_id": 1,
  "book_id": 1,
  "borrower_id": 1,
  "borrow_date": "2024-01-26T10:30:00",
  "return_date": "2024-01-26T15:45:00",
  "book": {...},
  "borrower": {...}
}
```

---

#### GET /transactions

Get all transactions.

**Query Parameters:**
- `skip` (int, optional): Skip N records (default: 0)
- `limit` (int, optional): Return N records (default: 100)

**Example Request:**
```bash
curl -X GET "http://localhost:8000/transactions?limit=20"
```

**Response:** `200 OK`
```json
[
  {
    "transaction_id": 1,
    "book_id": 1,
    "borrower_id": 1,
    "borrow_date": "2024-01-26T10:30:00",
    "return_date": "2024-01-26T15:45:00",
    ...
  }
]
```

---

### SEARCH

---

#### GET /search

Search books across all fields.

**Query Parameters:**
- `q` (string, required): Search keyword

**Searches across:**
- Title
- Author
- Category
- ISBN

**Example Request:**
```bash
curl -X GET "http://localhost:8000/search?q=python"
```

**Response:** `200 OK`
```json
[
  {
    "book_id": 4,
    "title": "Python Crash Course",
    "author": "Eric Matthes",
    "category": "Programming",
    "isbn": "9781593279288",
    "availability_status": "available"
  }
]
```

**No Results:**
```json
[]
```

---

### DASHBOARD

---

#### GET /dashboard

Get library statistics and recent activity.

**Example Request:**
```bash
curl -X GET "http://localhost:8000/dashboard"
```

**Response:** `200 OK`
```json
{
  "timestamp": "2024-01-26T10:30:00",
  "total_books": 5,
  "available_books": 4,
  "borrowed_books": 1,
  "total_borrowers": 3,
  "total_transactions": 10,
  "active_transactions": 2,
  "recent_transactions": [
    {
      "transaction_id": 10,
      "book_title": "Clean Code",
      "borrower_name": "Rahul Sharma",
      "borrow_date": "2024-01-26T09:00:00",
      "return_date": null,
      "status": "active"
    }
  ]
}
```

---

### HEALTH CHECK

---

#### GET /health

Check API health status.

**Example Request:**
```bash
curl -X GET "http://localhost:8000/health"
```

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "timestamp": "2024-01-26T10:30:00"
}
```

---

#### GET /

Root endpoint - API info.

**Response:**
```json
{
  "message": "Library Management System API v1.0 is running",
  "docs": "/docs",
  "redoc": "/redoc",
  "openapi": "/openapi.json",
  "status": "operational",
  "timestamp": "2024-01-26T10:30:00"
}
```

---

## HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource successfully created |
| 204 | No Content - Resource successfully deleted |
| 400 | Bad Request - Invalid request data |
| 404 | Not Found - Resource not found |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error - Server error |

---

## Error Handling

All errors follow a consistent format:

```json
{
  "detail": "Descriptive error message"
}
```

Common errors:

**Validation Error (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Not Found (404):**
```json
{
  "detail": "Book with ID 999 not found"
}
```

---

## Interactive API Documentation

Visit: `http://localhost:8000/docs`

Features:
- Test all endpoints directly from browser
- View request/response examples
- Auto-complete for parameters
- Pretty-printed JSON responses

---

## Rate Limiting

Phase 1 does NOT implement rate limiting.

---

## Pagination

For endpoints returning lists, use query parameters:

```
GET /books/?skip=0&limit=10
```

- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 100, max: 1000)

---

## Best Practices

1. **Always validate input** on client side
2. **Handle errors gracefully** in your frontend
3. **Cache responses** where appropriate
4. **Use pagination** for large datasets
5. **Test all endpoints** before deployment
6. **Monitor server logs** for errors

---

**API Documentation Generated**: January 26, 2024
**Version**: 1.0.0
