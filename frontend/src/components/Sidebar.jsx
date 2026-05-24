import React from 'react';

const navigationItems = [
  { path: '/', label: 'Dashboard', icon: '🏠' },
  { path: '/books', label: 'Books', icon: '📚' },
  { path: '/borrowers', label: 'Borrowers', icon: '👥' },
  { path: '/transactions', label: 'Transactions', icon: '🔄' },
  { path: '/search', label: 'Search', icon: '🔍' },
  { path: '/analytics', label: 'Analytics', icon: '📊' },
];

export default function Sidebar({ currentPath, onNavigate }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <span className="sidebar-icon">📖</span>
        <div>
          <div className="sidebar-title">LibraryMS</div>
          <div className="sidebar-subtitle">v2.0</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navigationItems.map((item) => (
          <button
            key={item.path}
            className={`nav-link ${currentPath === item.path ? 'active' : ''}`}
            onClick={() => onNavigate(item.path)}
            title={item.label}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <p>Phase 2 Project</p>
        <p>Capstone LMS</p>
      </div>
    </aside>
  );
}
