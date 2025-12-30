import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { PixelUsers, PixelChevron, PixelRocket, PixelCrown } from '../components/PixelIcons';
import './GameLobby.css';

interface Player {
  id: number;
  player_name: string;
  color: string;
  is_ai: boolean;
  ai_difficulty: string | null;
  is_ready: boolean;
  user_id: number | null;
}

interface Game {
  id: number;
  name: string;
  status: string;
  galaxy_shape: string;
  star_count: number;
  max_players: number;
  turn_duration_years: number;
  alliances_enabled: boolean;
  combat_luck_enabled: boolean;
  admin_id: number;
  players: Player[];
}

const SHAPE_LABELS: Record<string, string> = {
  circle: 'Cercle',
  spiral: 'Spirale',
  cluster: 'Amas',
  random: 'Aléatoire',
};

const DIFFICULTY_LABELS: Record<string, string> = {
  easy: 'Facile',
  medium: 'Moyen',
  hard: 'Difficile',
  expert: 'Expert',
};

function GameLobby() {
  const { gameId } = useParams<{ gameId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [game, setGame] = useState<Game | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const isAdmin = game?.admin_id === user?.id;
  const myPlayer = game?.players.find((p) => p.user_id === user?.id);
  const canStart = isAdmin && (game?.players.length || 0) >= 2;

  const loadGame = useCallback(async () => {
    if (!gameId) return;
    try {
      const data = await api.getGame(parseInt(gameId));
      setGame(data);

      // Redirect if game has started
      if (data.status === 'running') {
        navigate(`/games/${gameId}`);
      }
    } catch {
      setError('Partie non trouvée');
    } finally {
      setIsLoading(false);
    }
  }, [gameId, navigate]);

  useEffect(() => {
    loadGame();
    // Poll for updates every 3 seconds
    const interval = setInterval(loadGame, 3000);
    return () => clearInterval(interval);
  }, [loadGame]);

  const handleLeave = async () => {
    if (!gameId) return;
    setActionLoading('leave');
    try {
      await api.leaveGame(parseInt(gameId));
      navigate('/games');
    } catch {
      setError('Impossible de quitter la partie');
    } finally {
      setActionLoading(null);
    }
  };

  const handleDelete = async () => {
    if (!gameId || !confirm('Supprimer cette partie ?')) return;
    setActionLoading('delete');
    try {
      await api.deleteGame(parseInt(gameId));
      navigate('/games');
    } catch {
      setError('Impossible de supprimer la partie');
    } finally {
      setActionLoading(null);
    }
  };

  const handleAddAI = async (difficulty: string) => {
    if (!gameId) return;
    setActionLoading('ai');
    try {
      await api.addAIPlayer(parseInt(gameId), difficulty);
      await loadGame();
    } catch {
      setError("Impossible d'ajouter l'IA");
    } finally {
      setActionLoading(null);
    }
  };

  const handleRemoveAI = async (playerId: number) => {
    if (!gameId) return;
    setActionLoading(`remove-${playerId}`);
    try {
      await api.removeAIPlayer(parseInt(gameId), playerId);
      await loadGame();
    } catch {
      setError("Impossible de retirer l'IA");
    } finally {
      setActionLoading(null);
    }
  };

  const handleToggleReady = async () => {
    if (!gameId || !myPlayer) return;
    setActionLoading('ready');
    try {
      await api.setPlayerReady(parseInt(gameId), !myPlayer.is_ready);
      await loadGame();
    } catch {
      setError('Erreur lors du changement de statut');
    } finally {
      setActionLoading(null);
    }
  };

  const handleStartGame = async () => {
    if (!gameId) return;
    setActionLoading('start');
    try {
      await api.startGame(parseInt(gameId));
      navigate(`/games/${gameId}`);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Impossible de démarrer la partie';
      setError(errorMessage);
    } finally {
      setActionLoading(null);
    }
  };

  if (isLoading) {
    return (
      <div className="lobby-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Chargement du lobby...</p>
        </div>
      </div>
    );
  }

  if (error && !game) {
    return (
      <div className="lobby-page">
        <div className="error-container">
          <p>{error}</p>
          <button className="btn-primary" onClick={() => navigate('/games')}>
            Retour aux parties
          </button>
        </div>
      </div>
    );
  }

  if (!game) return null;

  const emptySlots = game.max_players - game.players.length;

  return (
    <div className="lobby-page">
      <div className="lobby-card">
        <div className="lobby-header">
          <button className="back-btn" onClick={() => navigate('/games')}>
            <PixelChevron size={16} direction="left" />
            Retour
          </button>
          <h1>{game.name}</h1>
          <span className="player-count">
            {game.players.length} / {game.max_players} joueurs
          </span>
        </div>

        {error && <div className="error-message">{error}</div>}

        <div className="lobby-content">
          <div className="players-section">
            <h2>
              <PixelUsers size={20} />
              Joueurs
            </h2>

            <div className="player-slots">
              {game.players.map((player) => (
                <div
                  key={player.id}
                  className={`player-slot ${player.is_ready ? 'ready' : ''}`}
                >
                  <div
                    className="player-color"
                    style={{ backgroundColor: player.color }}
                  />
                  <div className="player-info">
                    <span className="player-name">
                      {player.player_name}
                      {player.user_id === game.admin_id && (
                        <PixelCrown size={14} color="var(--orange-dark)" />
                      )}
                    </span>
                    {player.is_ai && (
                      <span className="player-badge ai">
                        IA {DIFFICULTY_LABELS[player.ai_difficulty || 'medium']}
                      </span>
                    )}
                  </div>
                  <div className="player-status">
                    {player.is_ai ? (
                      isAdmin && (
                        <button
                          className="remove-btn"
                          onClick={() => handleRemoveAI(player.id)}
                          disabled={actionLoading === `remove-${player.id}`}
                        >
                          ✕
                        </button>
                      )
                    ) : player.is_ready ? (
                      <span className="status-ready">Prêt</span>
                    ) : (
                      <span className="status-waiting">En attente</span>
                    )}
                  </div>
                </div>
              ))}

              {/* Empty slots */}
              {Array.from({ length: emptySlots }).map((_, i) => (
                <div key={`empty-${i}`} className="player-slot empty">
                  <div className="player-color empty" />
                  <div className="player-info">
                    <span className="player-name empty">En attente...</span>
                  </div>
                  {isAdmin && (
                    <div className="add-player-btns">
                      <select
                        className="add-ai-select"
                        onChange={(e) => {
                          if (e.target.value) {
                            handleAddAI(e.target.value);
                            e.target.value = '';
                          }
                        }}
                        disabled={actionLoading === 'ai'}
                      >
                        <option value="">+ IA</option>
                        <option value="easy">Facile</option>
                        <option value="medium">Moyen</option>
                        <option value="hard">Difficile</option>
                        <option value="expert">Expert</option>
                      </select>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="config-section">
            <h2>Configuration</h2>
            <div className="config-grid">
              <div className="config-item">
                <span className="config-label">Galaxie</span>
                <span className="config-value">
                  {SHAPE_LABELS[game.galaxy_shape]} • {game.star_count} étoiles
                </span>
              </div>
              <div className="config-item">
                <span className="config-label">Tours</span>
                <span className="config-value">{game.turn_duration_years} ans</span>
              </div>
              <div className="config-item">
                <span className="config-label">Alliances</span>
                <span className="config-value">
                  {game.alliances_enabled ? 'Activées' : 'Désactivées'}
                </span>
              </div>
              <div className="config-item">
                <span className="config-label">Chance</span>
                <span className="config-value">
                  {game.combat_luck_enabled ? 'Activée' : 'Désactivée'}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="lobby-actions">
          {isAdmin ? (
            <>
              <button
                className="btn-secondary"
                onClick={handleDelete}
                disabled={actionLoading === 'delete'}
              >
                Supprimer
              </button>
              <button
                className="btn-primary"
                onClick={handleStartGame}
                disabled={!canStart || actionLoading === 'start'}
              >
                {actionLoading === 'start' ? (
                  'Lancement...'
                ) : (
                  <>
                    <PixelRocket size={18} />
                    Lancer la partie
                  </>
                )}
              </button>
            </>
          ) : (
            <>
              <button
                className="btn-secondary"
                onClick={handleLeave}
                disabled={actionLoading === 'leave'}
              >
                Quitter
              </button>
              <button
                className={`btn-primary ${myPlayer?.is_ready ? 'ready' : ''}`}
                onClick={handleToggleReady}
                disabled={actionLoading === 'ready'}
              >
                {myPlayer?.is_ready ? 'Annuler' : 'Prêt'}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default GameLobby;
