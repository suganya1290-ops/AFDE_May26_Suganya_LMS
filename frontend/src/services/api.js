import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 5000,
});

// Error interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// ──────────────────────────────────────────────────────────────────────────────
// BOOK ENDPOINTS
// ──────────────────────────────────────────────────────────────────────────────

export const booksAPI = {
  getAll: (skip = 0, limit = 100) =>
    apiClient.get('/books/', { params: { skip, limit } }),
  getById: (id) => apiClient.get(`/books/${id}`),
  create: (data) => apiClient.post('/books/', data),
  update: (id, data) => apiClient.put(`/books/${id}`, data),
  delete: (id) => apiClient.delete(`/books/${id}`),
};

// ──────────────────────────────────────────────────────────────────────────────
// BORROWER ENDPOINTS
// ──────────────────────────────────────────────────────────────────────────────

export const borrowersAPI = {
  getAll: (skip = 0, limit = 100) =>
    apiClient.get('/borrowers/', { params: { skip, limit } }),
  getById: (id) => apiClient.get(`/borrowers/${id}`),
  create: (data) => apiClient.post('/borrowers/', data),
  update: (id, data) => apiClient.put(`/borrowers/${id}`, data),
  delete: (id) => apiClient.delete(`/borrowers/${id}`),
};

// ──────────────────────────────────────────────────────────────────────────────
// TRANSACTION ENDPOINTS
// ──────────────────────────────────────────────────────────────────────────────

export const transactionsAPI = {
  borrow: (bookId, borrowerId) =>
    apiClient.post('/borrow', { book_id: bookId, borrower_id: borrowerId }),
  return: (bookId, borrowerId) =>
    apiClient.post('/return', { book_id: bookId, borrower_id: borrowerId }),
  getAll: (skip = 0, limit = 100) =>
    apiClient.get('/transactions', { params: { skip, limit } }),
};

// ──────────────────────────────────────────────────────────────────────────────
// SEARCH ENDPOINTS
// ──────────────────────────────────────────────────────────────────────────────

export const searchAPI = {
  books: (query) => apiClient.get('/search', { params: { q: query } }),
};

// ──────────────────────────────────────────────────────────────────────────────
// DASHBOARD ENDPOINTS
// ──────────────────────────────────────────────────────────────────────────────

export const dashboardAPI = {
  getStats: () => apiClient.get('/dashboard'),
  health: () => apiClient.get('/health'),
};

// ──────────────────────────────────────────────────────────────────────────────
// ANALYTICS ENDPOINTS
// ──────────────────────────────────────────────────────────────────────────────

export const analyticsAPI = {
  getSummary: () => apiClient.get('/analytics/summary'),
  getPopularBooks: (limit = 10) => apiClient.get('/analytics/popular-books', { params: { limit } }),
  getCategoryStats: () => apiClient.get('/analytics/category-stats'),
  getMonthlyTrends: (year) => apiClient.get('/analytics/monthly-trends', { params: year ? { year } : {} }),
  getOverdue: () => apiClient.get('/analytics/overdue'),
};

// ──────────────────────────────────────────────────────────────────────────────
// ETL ENDPOINTS
// ──────────────────────────────────────────────────────────────────────────────

export const etlAPI = {
  runPipeline: () => apiClient.post('/etl/run', {}, { timeout: 60000 }),
  getLogs: () => apiClient.get('/etl/logs'),
  getStatus: () => apiClient.get('/etl/status'),
};

export default apiClient;
