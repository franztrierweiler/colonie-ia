import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './OAuthCallback.css';

function OAuthCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { setTokens } = useAuth();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const accessToken = searchParams.get('access_token');
    const refreshToken = searchParams.get('refresh_token');
    const errorParam = searchParams.get('error');

    if (errorParam) {
      setError('Erreur lors de la connexion avec Google');
      return;
    }

    if (accessToken && refreshToken) {
      // Stocker les tokens et rediriger
      setTokens(accessToken, refreshToken);
      navigate('/', { replace: true });
    } else {
      setError('Tokens manquants dans la réponse');
    }
  }, [searchParams, navigate, setTokens]);

  if (error) {
    return (
      <div className="oauth-callback">
        <div className="oauth-card">
          <div className="oauth-error">
            <h2>Erreur de connexion</h2>
            <p>{error}</p>
            <button onClick={() => navigate('/')} className="btn-primary">
              Retour à l'accueil
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="oauth-callback">
      <div className="oauth-card">
        <div className="oauth-loading">
          <div className="spinner"></div>
          <p>Connexion en cours...</p>
        </div>
      </div>
    </div>
  );
}

export default OAuthCallback;
