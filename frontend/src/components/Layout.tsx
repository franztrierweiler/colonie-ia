import { Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Layout.css';

function Layout() {
  const { isAuthenticated, user, logout, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner"></div>
        <p>Chargement...</p>
      </div>
    );
  }

  return (
    <div className="app-container">
      {isAuthenticated && (
        <header className="app-header">
          <div className="header-content">
            <span className="user-info">Général {user?.pseudo}</span>
            <button onClick={logout} className="btn-logout">
              Déconnexion
            </button>
          </div>
        </header>
      )}
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}

export default Layout;
