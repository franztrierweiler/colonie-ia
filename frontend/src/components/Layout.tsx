import { Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Layout.css';

function Layout() {
  const { isAuthenticated, user, logout, isLoading } = useAuth();
  const navigate = useNavigate();

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
            <div className="header-actions">
              <button onClick={() => navigate('/profile')} className="btn-header">
                Mon Profil
              </button>
              <button onClick={logout} className="btn-header btn-logout">
                Déconnexion
              </button>
            </div>
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
