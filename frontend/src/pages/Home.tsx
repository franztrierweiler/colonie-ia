import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

interface ApiStatus {
  status: string;
  service: string;
}

function Home() {
  const { isAuthenticated, user } = useAuth();
  const [apiStatus, setApiStatus] = useState<ApiStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    checkApiStatus();
  }, []);

  const checkApiStatus = async () => {
    try {
      const status = await api.health();
      setApiStatus(status);
      setError(null);
    } catch {
      setError('API non disponible');
      setApiStatus(null);
    }
  };

  return (
    <div className="home-page">
      <section className="hero">
        <h2>Conquete Galactique</h2>
        <p className="subtitle">
          Un jeu de strategie 4X au tour par tour, theme Empire Napoleonien
        </p>
      </section>

      {isAuthenticated ? (
        <section className="dashboard">
          <h3>Bienvenue, {user?.pseudo} !</h3>
          <div className="actions">
            <button className="btn-primary">Nouvelle Partie</button>
            <button className="btn-secondary">Rejoindre une Partie</button>
          </div>
        </section>
      ) : (
        <section className="cta">
          <p>Connectez-vous pour commencer a jouer</p>
        </section>
      )}

      <section className="api-status">
        <h4>Statut API</h4>
        {error ? (
          <p className="status-error">{error}</p>
        ) : apiStatus ? (
          <p className="status-ok">
            {apiStatus.service}: {apiStatus.status}
          </p>
        ) : (
          <p>Verification...</p>
        )}
      </section>
    </div>
  );
}

export default Home;
