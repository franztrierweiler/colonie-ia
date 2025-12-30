import { useState, useRef, useEffect } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { PixelUser, PixelLogout, PixelChevron } from './PixelIcons';
import './Layout.css';

function Layout() {
  const { isAuthenticated, user, logout, isLoading } = useAuth();
  const navigate = useNavigate();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    setDropdownOpen(false);
    logout();
  };

  const handleProfileClick = () => {
    setDropdownOpen(false);
    navigate('/profile');
  };

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
            <div className="header-logo" onClick={() => navigate('/')}>
              <img src="/game-logo.jpg" alt="Colonie-IA" className="header-logo-img" />
              <span className="header-logo-text">Colonie-IA</span>
            </div>
            <div className="header-right">
              <div className="profile-dropdown" ref={dropdownRef}>
                <button
                  className="profile-trigger"
                  onClick={() => setDropdownOpen(!dropdownOpen)}
                >
                  {user?.avatar_url ? (
                    <img src={user.avatar_url} alt="" className="profile-avatar" />
                  ) : (
                    <div className="profile-avatar-placeholder">
                      {user?.pseudo?.charAt(0).toUpperCase() || 'U'}
                    </div>
                  )}
                  <span className="profile-name">{user?.pseudo}</span>
                  <PixelChevron
                    className={`dropdown-arrow ${dropdownOpen ? 'open' : ''}`}
                    size={12}
                    direction={dropdownOpen ? 'up' : 'down'}
                  />
                </button>
                {dropdownOpen && (
                  <div className="dropdown-menu">
                    <div className="dropdown-header">
                      <span className="dropdown-label">Connecté en tant que</span>
                      <span className="dropdown-user">{user?.pseudo}</span>
                    </div>
                    <div className="dropdown-divider"></div>
                    <button className="dropdown-item" onClick={handleProfileClick}>
                      <PixelUser size={16} />
                      Mon Profil
                    </button>
                    <div className="dropdown-divider"></div>
                    <button className="dropdown-item dropdown-item-danger" onClick={handleLogout}>
                      <PixelLogout size={16} />
                      Déconnexion
                    </button>
                  </div>
                )}
              </div>
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
