import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Profile.css';

type Section = 'profile' | 'games' | 'messages' | 'account';

export default function Profile() {
  const { user, updateProfile, deleteAccount } = useAuth();
  const navigate = useNavigate();
  const [activeSection, setActiveSection] = useState<Section>('profile');
  const [pseudo, setPseudo] = useState(user?.pseudo || '');
  const [avatarUrl, setAvatarUrl] = useState(user?.avatar_url || '');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setIsLoading(true);

    try {
      await updateProfile({
        pseudo: pseudo !== user?.pseudo ? pseudo : undefined,
        avatar_url: avatarUrl !== user?.avatar_url ? avatarUrl : undefined,
      });
      setSuccess('Profil mis à jour');
    } catch (err: unknown) {
      const error = err as { response?: { data?: { error?: string } } };
      setError(error.response?.data?.error || 'Erreur lors de la mise à jour');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (deleteConfirmText !== 'SUPPRIMER') return;

    setIsLoading(true);
    setError('');

    try {
      await deleteAccount();
      navigate('/');
    } catch (err: unknown) {
      const error = err as { response?: { data?: { error?: string } } };
      setError(error.response?.data?.error || 'Erreur lors de la suppression');
      setIsLoading(false);
    }
  };

  const menuItems: { key: Section; label: string; icon: string }[] = [
    { key: 'profile', label: 'Profil', icon: '👤' },
    { key: 'games', label: 'Mes parties', icon: '🎮' },
    { key: 'messages', label: 'Messages', icon: '💬' },
    { key: 'account', label: 'Compte', icon: '⚙️' },
  ];

  return (
    <div className="settings-container">
      <aside className="settings-sidebar">
        <nav className="settings-nav">
          {menuItems.map((item) => (
            <button
              key={item.key}
              className={`settings-nav-item ${activeSection === item.key ? 'active' : ''}`}
              onClick={() => setActiveSection(item.key)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </button>
          ))}
        </nav>
      </aside>

      <main className="settings-content">
        {activeSection === 'profile' && (
          <div className="settings-section">
            <h2>Profil public</h2>
            <p className="section-description">Ces informations sont visibles par les autres joueurs.</p>

            {error && <div className="settings-error">{error}</div>}
            {success && <div className="settings-success">{success}</div>}

            <form onSubmit={handleSubmit} className="settings-form">
              <div className="form-group">
                <label htmlFor="pseudo">Pseudo</label>
                <input
                  type="text"
                  id="pseudo"
                  value={pseudo}
                  onChange={(e) => setPseudo(e.target.value)}
                  minLength={3}
                  maxLength={30}
                />
                <span className="form-hint">3 à 30 caractères, lettres, chiffres, espaces, tirets</span>
              </div>

              <div className="form-group">
                <label htmlFor="avatarUrl">URL de l'avatar</label>
                <div className="avatar-input-group">
                  {avatarUrl && (
                    <img src={avatarUrl} alt="Avatar" className="avatar-preview" />
                  )}
                  <input
                    type="url"
                    id="avatarUrl"
                    value={avatarUrl}
                    onChange={(e) => setAvatarUrl(e.target.value)}
                    placeholder="https://..."
                  />
                </div>
                <span className="form-hint">URL d'une image (PNG, JPG)</span>
              </div>

              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input
                  type="email"
                  id="email"
                  value={user?.email || ''}
                  disabled
                  className="input-disabled"
                />
                <span className="form-hint">L'email ne peut pas être modifié</span>
              </div>

              <div className="form-actions">
                <button type="submit" className="btn-save" disabled={isLoading}>
                  {isLoading ? 'Enregistrement...' : 'Enregistrer'}
                </button>
                <button type="button" className="btn-back" onClick={() => navigate(-1)}>
                  Retour
                </button>
              </div>
            </form>
          </div>
        )}

        {activeSection === 'games' && (
          <div className="settings-section">
            <h2>Mes parties</h2>
            <p className="section-description">Historique de vos parties et statistiques.</p>
            <div className="empty-state">
              <span className="empty-icon">🎮</span>
              <p>Aucune partie pour le moment</p>
              <span className="empty-hint">Créez ou rejoignez une partie depuis l'accueil</span>
            </div>
          </div>
        )}

        {activeSection === 'messages' && (
          <div className="settings-section">
            <h2>Messages</h2>
            <p className="section-description">Vos messages et notifications.</p>
            <div className="empty-state">
              <span className="empty-icon">💬</span>
              <p>Aucun message</p>
              <span className="empty-hint">Les messages des autres joueurs apparaîtront ici</span>
            </div>
          </div>
        )}

        {activeSection === 'account' && (
          <div className="settings-section">
            <h2>Gestion du compte</h2>
            <p className="section-description">Paramètres et suppression de votre compte.</p>

            {error && <div className="settings-error">{error}</div>}

            <div className="danger-zone">
              <h3>Zone de danger</h3>
              <div className="danger-item">
                <div className="danger-info">
                  <strong>Supprimer le compte</strong>
                  <p>Cette action est irréversible. Toutes vos données seront anonymisées conformément au RGPD.</p>
                </div>
                <button
                  className="btn-danger"
                  onClick={() => setShowDeleteConfirm(true)}
                >
                  Supprimer mon compte
                </button>
              </div>
            </div>

            {showDeleteConfirm && (
              <div className="delete-confirm-overlay">
                <div className="delete-confirm-modal">
                  <h3>Confirmer la suppression</h3>
                  <p>Cette action est <strong>définitive</strong>. Votre compte et toutes vos données seront supprimés.</p>
                  <p>Pour confirmer, tapez <strong>SUPPRIMER</strong> ci-dessous :</p>
                  <input
                    type="text"
                    value={deleteConfirmText}
                    onChange={(e) => setDeleteConfirmText(e.target.value)}
                    placeholder="SUPPRIMER"
                    autoFocus
                  />
                  <div className="delete-confirm-actions">
                    <button
                      className="btn-danger"
                      onClick={handleDeleteAccount}
                      disabled={deleteConfirmText !== 'SUPPRIMER' || isLoading}
                    >
                      {isLoading ? 'Suppression...' : 'Confirmer la suppression'}
                    </button>
                    <button
                      className="btn-back"
                      onClick={() => {
                        setShowDeleteConfirm(false);
                        setDeleteConfirmText('');
                      }}
                    >
                      Annuler
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
