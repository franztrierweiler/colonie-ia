import { Outlet, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Layout() {
  const { isAuthenticated, user, logout, isLoading } = useAuth();

  if (isLoading) {
    return <div className="loading">Chargement...</div>;
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <nav>
          <Link to="/" className="logo-link">
            <h1>Colonie-IA</h1>
          </Link>
          <div className="nav-links">
            {isAuthenticated ? (
              <>
                <span className="user-pseudo">{user?.pseudo}</span>
                <button onClick={logout} className="btn-logout">
                  Deconnexion
                </button>
              </>
            ) : (
              <>
                <Link to="/login">Connexion</Link>
                <Link to="/register" className="btn-register">
                  Inscription
                </Link>
              </>
            )}
          </div>
        </nav>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
      <footer className="app-footer">
        <p>Colonie-IA - Jeu de strategie 4X galactique</p>
      </footer>
    </div>
  );
}

export default Layout;
