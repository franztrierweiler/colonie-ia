import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { PixelRocket, PixelUsers, PixelStar } from '../components/PixelIcons';
import './GameList.css';

interface Game {
  id: number;
  name: string;
  status: string;
  galaxy_shape: string;
  star_count: number;
  max_players: number;
  player_count: number;
  admin_id: number;
  created_at: string;
}

function GameList() {
  const navigate = useNavigate();
  const [games, setGames] = useState<Game[]>([]);
  const [myGames, setMyGames] = useState<Game[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'lobby' | 'my'>('lobby');

  useEffect(() => {
    loadGames();
  }, []);

  const loadGames = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [lobbyResponse, myResponse] = await Promise.all([
        api.listGames(),
        api.getMyGames(),
      ]);
      setGames(lobbyResponse.games || []);
      setMyGames(myResponse.games || []);
    } catch {
      setError('Erreur lors du chargement des parties');
    } finally {
      setIsLoading(false);
    }
  };

  const handleJoinGame = async (gameId: number) => {
    try {
      await api.joinGame(gameId);
      navigate(`/games/${gameId}/lobby`);
    } catch {
      setError('Impossible de rejoindre la partie');
    }
  };

  const getShapeLabel = (shape: string) => {
    const labels: Record<string, string> = {
      circle: 'Cercle',
      spiral: 'Spirale',
      cluster: 'Amas',
      random: 'Aléatoire',
    };
    return labels[shape] || shape;
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      lobby: 'En attente',
      running: 'En cours',
      finished: 'Terminée',
      abandoned: 'Abandonnée',
    };
    return labels[status] || status;
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const displayedGames = activeTab === 'lobby' ? games : myGames;

  return (
    <div className="game-list-page">
      <div className="game-list-header">
        <h1>Parties</h1>
        <button
          className="btn-primary create-game-btn"
          onClick={() => navigate('/games/new')}
        >
          <PixelRocket size={20} />
          Nouvelle Partie
        </button>
      </div>

      <div className="game-list-tabs">
        <button
          className={`tab ${activeTab === 'lobby' ? 'active' : ''}`}
          onClick={() => setActiveTab('lobby')}
        >
          <PixelUsers size={16} />
          En attente ({games.length})
        </button>
        <button
          className={`tab ${activeTab === 'my' ? 'active' : ''}`}
          onClick={() => setActiveTab('my')}
        >
          <PixelStar size={16} />
          Mes parties ({myGames.length})
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {isLoading ? (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Chargement des parties...</p>
        </div>
      ) : displayedGames.length === 0 ? (
        <div className="empty-state">
          <PixelStar size={48} color="var(--text-muted)" />
          <h3>Aucune partie disponible</h3>
          <p>
            {activeTab === 'lobby'
              ? 'Créez une nouvelle partie pour commencer la conquête !'
              : "Vous n'avez pas encore de parties en cours."}
          </p>
          {activeTab === 'lobby' && (
            <button
              className="btn-primary"
              onClick={() => navigate('/games/new')}
            >
              Créer une partie
            </button>
          )}
        </div>
      ) : (
        <div className="game-cards">
          {displayedGames.map((game) => (
            <div key={game.id} className="game-card">
              <div className="game-card-header">
                <h3 className="game-name">{game.name}</h3>
                <span className={`game-status status-${game.status}`}>
                  {getStatusLabel(game.status)}
                </span>
              </div>

              <div className="game-card-info">
                <div className="info-row">
                  <span className="info-label">Galaxie</span>
                  <span className="info-value">
                    {getShapeLabel(game.galaxy_shape)} • {game.star_count} étoiles
                  </span>
                </div>
                <div className="info-row">
                  <span className="info-label">Joueurs</span>
                  <span className="info-value">
                    {game.player_count} / {game.max_players}
                  </span>
                </div>
                <div className="info-row">
                  <span className="info-label">Créée le</span>
                  <span className="info-value">{formatDate(game.created_at)}</span>
                </div>
              </div>

              <div className="game-card-actions">
                {game.status === 'lobby' && activeTab === 'lobby' && (
                  <button
                    className="btn-primary"
                    onClick={() => handleJoinGame(game.id)}
                    disabled={game.player_count >= game.max_players}
                  >
                    {game.player_count >= game.max_players ? 'Complet' : 'Rejoindre'}
                  </button>
                )}
                {activeTab === 'my' && (
                  <button
                    className="btn-primary"
                    onClick={() =>
                      navigate(
                        game.status === 'lobby'
                          ? `/games/${game.id}/lobby`
                          : `/games/${game.id}`
                      )
                    }
                  >
                    {game.status === 'lobby' ? 'Voir le lobby' : 'Continuer'}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default GameList;
