import React, { useState, useEffect, useCallback } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
  LineChart, Line,
} from 'recharts';
import { analyticsAPI, etlAPI } from '../services/api';

const COLORS = ['#4f8ef7', '#34c97b', '#f7a94f', '#f76e6e', '#b16ef7', '#4fc7f7', '#f7e24f', '#7ef7c4', '#f77eb1', '#a0f74f'];

const CARD_STYLE = {
  background: '#fff',
  borderRadius: 10,
  padding: '20px 24px',
  boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
  marginBottom: 24,
};

const SECTION_TITLE = {
  fontSize: '1rem',
  fontWeight: 600,
  marginBottom: 16,
  color: '#1a202c',
};

const StatCard = ({ label, value, color }) => (
  <div style={{ ...CARD_STYLE, borderLeft: `4px solid ${color}`, marginBottom: 0, flex: 1 }}>
    <div style={{ fontSize: '0.78rem', color: '#718096', textTransform: 'uppercase', letterSpacing: 1 }}>{label}</div>
    <div style={{ fontSize: '2rem', fontWeight: 700, color, marginTop: 4 }}>{value ?? '—'}</div>
  </div>
);

export default function Analytics() {
  const [summary, setSummary] = useState(null);
  const [popularBooks, setPopularBooks] = useState([]);
  const [categoryStats, setCategoryStats] = useState([]);
  const [monthlyTrends, setMonthlyTrends] = useState([]);
  const [overdueList, setOverdueList] = useState([]);
  const [etlStatus, setEtlStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState(null);
  const [selectedYear, setSelectedYear] = useState('all');

  const fetchAll = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [sumRes, popRes, catRes, trendRes, overdueRes, statusRes] = await Promise.all([
        analyticsAPI.getSummary(),
        analyticsAPI.getPopularBooks(10),
        analyticsAPI.getCategoryStats(),
        analyticsAPI.getMonthlyTrends(),
        analyticsAPI.getOverdue(),
        etlAPI.getStatus(),
      ]);
      setSummary(sumRes.data);
      setPopularBooks(popRes.data);
      setCategoryStats(catRes.data);
      setMonthlyTrends(trendRes.data);
      setOverdueList(overdueRes.data);
      setEtlStatus(statusRes.data);
    } catch (err) {
      setError('Analytics data not available. Run the ETL pipeline first.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const handleRunETL = async () => {
    setRunning(true);
    try {
      await etlAPI.runPipeline();
      await fetchAll();
    } catch (err) {
      setError('ETL pipeline failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setRunning(false);
    }
  };

  const availableYears = [...new Set(monthlyTrends.map(r => r.year))].sort();
  const filteredTrends = selectedYear === 'all'
    ? monthlyTrends
    : monthlyTrends.filter(r => r.year === parseInt(selectedYear));

  const formatLabel = (entry) => `${entry.name}: ${entry.value}`;

  return (
    <div style={{ padding: '28px 32px', maxWidth: 1200 }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#1a202c', margin: 0 }}>
            Analytics Dashboard
          </h1>
          <p style={{ color: '#718096', marginTop: 4, fontSize: '0.88rem' }}>
            ETL-powered insights — borrowing trends, popular books, overdue analysis
          </p>
        </div>
        <button
          onClick={handleRunETL}
          disabled={running}
          style={{
            background: running ? '#b0c4de' : '#4f8ef7',
            color: '#fff',
            border: 'none',
            borderRadius: 8,
            padding: '10px 20px',
            cursor: running ? 'not-allowed' : 'pointer',
            fontWeight: 600,
            fontSize: '0.9rem',
          }}
        >
          {running ? 'Running ETL...' : 'Run ETL Pipeline'}
        </button>
      </div>

      {/* ETL Status Bar */}
      {etlStatus && etlStatus.status !== 'never_run' && (
        <div style={{
          background: etlStatus.status === 'success' ? '#f0fff4' : '#fff5f5',
          border: `1px solid ${etlStatus.status === 'success' ? '#34c97b' : '#f76e6e'}`,
          borderRadius: 8, padding: '10px 16px', marginBottom: 20,
          fontSize: '0.83rem', color: '#4a5568',
          display: 'flex', gap: 24, flexWrap: 'wrap',
        }}>
          <span><strong>Last ETL Run:</strong> {new Date(etlStatus.run_at).toLocaleString()}</span>
          <span><strong>Status:</strong> <span style={{ color: etlStatus.status === 'success' ? '#34c97b' : '#f76e6e', fontWeight: 600 }}>{etlStatus.status}</span></span>
          <span><strong>Extracted:</strong> {etlStatus.records_extracted}</span>
          <span><strong>Transformed:</strong> {etlStatus.records_transformed}</span>
          <span><strong>Loaded:</strong> {etlStatus.records_loaded}</span>
          <span><strong>Duration:</strong> {etlStatus.duration_seconds}s</span>
        </div>
      )}

      {error && (
        <div style={{ background: '#fff5f5', border: '1px solid #f76e6e', borderRadius: 8, padding: '12px 16px', marginBottom: 20, color: '#c53030' }}>
          {error}
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: 60, color: '#718096' }}>Loading analytics...</div>
      ) : (
        <>
          {/* Summary Cards */}
          {summary && (
            <div style={{ display: 'flex', gap: 16, marginBottom: 24, flexWrap: 'wrap' }}>
              <StatCard label="Total Transactions Analyzed" value={summary.total_transactions_analyzed} color="#4f8ef7" />
              <StatCard label="Overdue Books" value={summary.overdue_count} color="#f76e6e" />
              <StatCard label="Categories Tracked" value={summary.categories_tracked} color="#b16ef7" />
              <StatCard label="Top Book Borrows" value={summary.top_book_borrows} color="#34c97b" />
            </div>
          )}

          {summary && (
            <div style={{ display: 'flex', gap: 16, marginBottom: 24, flexWrap: 'wrap' }}>
              <div style={{ ...CARD_STYLE, flex: 1, marginBottom: 0, background: 'linear-gradient(135deg,#4f8ef7 0%,#b16ef7 100%)', color: '#fff' }}>
                <div style={{ fontSize: '0.75rem', opacity: 0.85, textTransform: 'uppercase', letterSpacing: 1 }}>Most Borrowed Book</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 700, marginTop: 4 }}>{summary.top_book}</div>
              </div>
              <div style={{ ...CARD_STYLE, flex: 1, marginBottom: 0, background: 'linear-gradient(135deg,#34c97b 0%,#4fc7f7 100%)', color: '#fff' }}>
                <div style={{ fontSize: '0.75rem', opacity: 0.85, textTransform: 'uppercase', letterSpacing: 1 }}>Top Category</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 700, marginTop: 4 }}>{summary.top_category} ({summary.top_category_borrowings} borrows)</div>
              </div>
            </div>
          )}

          {/* Row: Popular Books + Category Pie */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 24 }}>
            {/* Popular Books Bar Chart */}
            <div style={CARD_STYLE}>
              <div style={SECTION_TITLE}>Top 10 Most Borrowed Books</div>
              {popularBooks.length === 0 ? (
                <p style={{ color: '#718096' }}>No data. Run the ETL pipeline.</p>
              ) : (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={popularBooks} layout="vertical" margin={{ left: 10, right: 20, top: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                    <XAxis type="number" tick={{ fontSize: 11 }} />
                    <YAxis
                      dataKey="title"
                      type="category"
                      width={130}
                      tick={{ fontSize: 10 }}
                      tickFormatter={(v) => v.length > 20 ? v.slice(0, 18) + '…' : v}
                    />
                    <Tooltip
                      formatter={(value) => [value, 'Borrows']}
                      labelFormatter={(label) => label}
                    />
                    <Bar dataKey="total_borrows" fill="#4f8ef7" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>

            {/* Category Pie Chart */}
            <div style={CARD_STYLE}>
              <div style={SECTION_TITLE}>Category-wise Borrowing Distribution</div>
              {categoryStats.length === 0 ? (
                <p style={{ color: '#718096' }}>No data. Run the ETL pipeline.</p>
              ) : (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={categoryStats}
                      dataKey="total_borrowings"
                      nameKey="category"
                      cx="50%"
                      cy="45%"
                      outerRadius={100}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      labelLine={false}
                    >
                      {categoryStats.map((_, i) => (
                        <Cell key={i} fill={COLORS[i % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={formatLabel} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>

          {/* Monthly Trends Line Chart */}
          <div style={CARD_STYLE}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <div style={SECTION_TITLE}>Monthly Borrowing Trends</div>
              <select
                value={selectedYear}
                onChange={(e) => setSelectedYear(e.target.value)}
                style={{ border: '1px solid #e2e8f0', borderRadius: 6, padding: '4px 10px', fontSize: '0.85rem', color: '#4a5568' }}
              >
                <option value="all">All Years</option>
                {availableYears.map(y => (
                  <option key={y} value={y}>{y}</option>
                ))}
              </select>
            </div>
            {filteredTrends.length === 0 ? (
              <p style={{ color: '#718096' }}>No trend data. Run the ETL pipeline.</p>
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={filteredTrends} margin={{ left: 0, right: 20, top: 5, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="label" tick={{ fontSize: 10 }} interval={1} angle={-30} textAnchor="end" height={50} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="total_borrowings" stroke="#4f8ef7" strokeWidth={2} dot={{ r: 3 }} name="Borrowings" />
                  <Line type="monotone" dataKey="total_returns" stroke="#34c97b" strokeWidth={2} dot={{ r: 3 }} name="Returns" />
                  <Line type="monotone" dataKey="active_loans" stroke="#f7a94f" strokeWidth={2} dot={{ r: 3 }} name="Active" strokeDasharray="5 5" />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>

          {/* Category Stats Table */}
          <div style={CARD_STYLE}>
            <div style={SECTION_TITLE}>Category Borrowing Statistics</div>
            {categoryStats.length === 0 ? (
              <p style={{ color: '#718096' }}>No data. Run the ETL pipeline.</p>
            ) : (
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.88rem' }}>
                <thead>
                  <tr style={{ background: '#f7fafc' }}>
                    {['Category', 'Total Borrowings', 'Unique Borrowers', 'Avg Loan Days'].map(h => (
                      <th key={h} style={{ padding: '10px 14px', textAlign: 'left', fontWeight: 600, color: '#4a5568', borderBottom: '2px solid #e2e8f0' }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {categoryStats.map((r, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid #e2e8f0' }}>
                      <td style={{ padding: '9px 14px', fontWeight: 500 }}>{r.category}</td>
                      <td style={{ padding: '9px 14px' }}>{r.total_borrowings}</td>
                      <td style={{ padding: '9px 14px' }}>{r.unique_borrowers}</td>
                      <td style={{ padding: '9px 14px' }}>{r.avg_loan_days} days</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {/* Overdue Transactions Table */}
          <div style={CARD_STYLE}>
            <div style={{ ...SECTION_TITLE, color: '#c53030' }}>
              Overdue Transactions ({overdueList.length})
            </div>
            {overdueList.length === 0 ? (
              <p style={{ color: '#718096' }}>No overdue transactions found.</p>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.86rem' }}>
                  <thead>
                    <tr style={{ background: '#fff5f5' }}>
                      {['#', 'Book', 'Borrower', 'Borrowed On', 'Due Date', 'Days Overdue'].map(h => (
                        <th key={h} style={{ padding: '10px 12px', textAlign: 'left', fontWeight: 600, color: '#c53030', borderBottom: '2px solid #fed7d7' }}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {overdueList.map((r, i) => (
                      <tr key={i} style={{ borderBottom: '1px solid #fed7d7', background: i % 2 === 0 ? '#fff' : '#fffafa' }}>
                        <td style={{ padding: '8px 12px', color: '#718096' }}>{r.transaction_id}</td>
                        <td style={{ padding: '8px 12px', fontWeight: 500 }}>{r.book_title}</td>
                        <td style={{ padding: '8px 12px' }}>{r.borrower_name}</td>
                        <td style={{ padding: '8px 12px' }}>{r.borrow_date ? new Date(r.borrow_date).toLocaleDateString() : '—'}</td>
                        <td style={{ padding: '8px 12px' }}>{r.due_date ? new Date(r.due_date).toLocaleDateString() : '—'}</td>
                        <td style={{ padding: '8px 12px' }}>
                          <span style={{ background: '#fed7d7', color: '#c53030', padding: '2px 8px', borderRadius: 12, fontWeight: 700, fontSize: '0.8rem' }}>
                            {r.days_overdue} days
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
