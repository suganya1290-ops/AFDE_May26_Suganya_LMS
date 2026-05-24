import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Books from './pages/Books';
import Borrowers from './pages/Borrowers';
import Transactions from './pages/Transactions';
import Search from './pages/Search';
import Analytics from './pages/Analytics';
import './App.css';

export default function App() {
  const [currentPath, setCurrentPath] = useState('/');

  const renderPage = () => {
    switch (currentPath) {
      case '/':
        return <Dashboard />;
      case '/books':
        return <Books />;
      case '/borrowers':
        return <Borrowers />;
      case '/transactions':
        return <Transactions />;
      case '/search':
        return <Search />;
      case '/analytics':
        return <Analytics />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="app-container">
      <Sidebar currentPath={currentPath} onNavigate={setCurrentPath} />
      <main className="main-content">
        {renderPage()}
      </main>
    </div>
  );
}
