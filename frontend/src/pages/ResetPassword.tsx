import { useState } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import './ResetPassword.css';

function ResetPassword() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      return;
    }

    if (password.length < 8) {
      setError('Le mot de passe doit contenir au moins 8 caractères');
      return;
    }

    if (!token) {
      setError('Token de réinitialisation manquant');
      return;
    }

    setIsLoading(true);

    try {
      await api.resetPassword(token, password);
      setSuccess(true);
    } catch {
      setError('Token invalide ou expiré. Veuillez refaire une demande.');
    } finally {
      setIsLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="reset-container">
        <div className="reset-card">
          <div className="reset-error-state">
            <h2>Lien invalide</h2>
            <p>Ce lien de réinitialisation est invalide ou a expiré.</p>
            <Link to="/forgot-password" className="btn-primary">
              Demander un nouveau lien
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="reset-container">
      <div className="reset-card">
        <div className="reset-header">
          <h1>Nouveau mot de passe</h1>
          <p>Choisissez un nouveau mot de passe sécurisé.</p>
        </div>

        {success ? (
          <div className="reset-success">
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
              <circle cx="24" cy="24" r="20" stroke="currentColor" strokeWidth="2"/>
              <path d="M16 24L22 30L32 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <h2>Mot de passe modifié !</h2>
            <p>Vous pouvez maintenant vous connecter avec votre nouveau mot de passe.</p>
            <button onClick={() => navigate('/')} className="btn-primary">
              Se connecter
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="reset-form">
            {error && <div className="reset-error">{error}</div>}

            <div className="form-group">
              <label htmlFor="password">Nouveau mot de passe</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                minLength={8}
              />
              <span className="form-hint">
                8 caractères minimum, avec majuscule, minuscule et chiffre
              </span>
            </div>

            <div className="form-group">
              <label htmlFor="confirmPassword">Confirmer le mot de passe</label>
              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>

            <button type="submit" className="btn-primary btn-submit" disabled={isLoading}>
              {isLoading ? 'Modification...' : 'Modifier le mot de passe'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}

export default ResetPassword;
