import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { GalaxyMap } from '../components/game';
import type { Star, Fleet, Player, Galaxy } from '../hooks/useGameState';
import './GameView.css';

interface GameMapData {
  game_id: number;
  turn: number;
  my_player_id: number;
  galaxy: Galaxy;
  stars: Star[];
  fleets: Fleet[];
  players: Player[];
}

function GameView() {
  const { gameId } = useParams<{ gameId: string }>();
  const navigate = useNavigate();

  const [mapData, setMapData] = useState<GameMapData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedStarId, setSelectedStarId] = useState<number | null>(null);
  const [selectedFleetId, setSelectedFleetId] = useState<number | null>(null);

  const loadMap = useCallback(async () => {
    if (!gameId) return;
    try {
      const data = await api.getGameMap(parseInt(gameId));
      setMapData(data);
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erreur de chargement';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [gameId]);

  useEffect(() => {
    loadMap();
  }, [loadMap]);

  const handleStarClick = (starId: number) => {
    setSelectedStarId(starId === selectedStarId ? null : starId);
    setSelectedFleetId(null);
  };

  const handleFleetClick = (fleetId: number) => {
    setSelectedFleetId(fleetId === selectedFleetId ? null : fleetId);
  };

  const getPlayerColor = (playerId: number | null): string => {
    if (!playerId || !mapData) return '#666';
    const player = mapData.players.find((p) => p.id === playerId);
    return player?.color || '#666';
  };

  const selectedStar = mapData?.stars.find((s) => s.id === selectedStarId);
  const selectedFleet = mapData?.fleets.find((f) => f.id === selectedFleetId);

  if (isLoading) {
    return (
      <div className="game-view">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Chargement de la galaxie...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="game-view">
        <div className="error-container">
          <p>{error}</p>
          <button className="btn-primary" onClick={() => navigate('/games')}>
            Retour aux parties
          </button>
        </div>
      </div>
    );
  }

  if (!mapData) return null;

  return (
    <div className="game-view">
      {/* Header */}
      <header className="game-header">
        <button className="btn-back" onClick={() => navigate('/games')}>
          Quitter
        </button>
        <h1>Tour {mapData.turn}</h1>
        <div className="turn-actions">
          <button className="btn-primary" onClick={loadMap}>
            Rafraîchir
          </button>
          <button className="btn-primary">Fin de tour</button>
        </div>
      </header>

      {/* Main content */}
      <div className="game-content">
        {/* Galaxy Map */}
        <GalaxyMap
          width={mapData.galaxy.width}
          height={mapData.galaxy.height}
          stars={mapData.stars}
          fleets={mapData.fleets}
          players={mapData.players}
          myPlayerId={mapData.my_player_id}
          selectedStarId={selectedStarId}
          onStarClick={handleStarClick}
          onFleetClick={handleFleetClick}
        />

        {/* Side Panel */}
        <aside className="side-panel">
          {selectedFleet ? (
            // Fleet details
            <div className="fleet-info">
              <div className="panel-header">
                <h2>{selectedFleet.name}</h2>
                <button
                  className="close-btn"
                  onClick={() => setSelectedFleetId(null)}
                >
                  ×
                </button>
              </div>
              <div className="fleet-details">
                <p>
                  <strong>Vaisseaux:</strong> {selectedFleet.ship_count}
                </p>
                <p>
                  <strong>Vitesse:</strong> {selectedFleet.fleet_speed.toFixed(1)}
                </p>
                <p>
                  <strong>Portée:</strong> {selectedFleet.fleet_range.toFixed(1)}
                </p>
                <p>
                  <strong>Statut:</strong>{' '}
                  {selectedFleet.status === 'stationed' ? 'En orbite' : 'En transit'}
                </p>
              </div>
            </div>
          ) : selectedStar ? (
            // Star details
            <div className="star-info">
              <div className="panel-header">
                <h2>{selectedStar.name}</h2>
                <button
                  className="close-btn"
                  onClick={() => setSelectedStarId(null)}
                >
                  ×
                </button>
              </div>
              <p className="star-coords">
                Position: ({selectedStar.x.toFixed(1)}, {selectedStar.y.toFixed(1)})
              </p>

              <h3>Planètes ({selectedStar.planets.length})</h3>
              <div className="planets-list">
                {selectedStar.planets.map((planet) => (
                  <div
                    key={planet.id}
                    className={`planet-card ${planet.owner_id === mapData.my_player_id ? 'owned' : ''} ${planet.state === 'unexplored' ? 'unexplored' : ''}`}
                  >
                    <div className="planet-header">
                      <span className="planet-name">
                        {planet.state === 'unexplored' ? '???' : planet.name}
                      </span>
                      {planet.owner_id && (
                        <span
                          className="owner-dot"
                          style={{ backgroundColor: getPlayerColor(planet.owner_id) }}
                        />
                      )}
                      {planet.is_home_planet && (
                        <span className="home-badge" title="Planète mère">H</span>
                      )}
                    </div>
                    {planet.state !== 'unexplored' && (
                      <>
                        <div className="planet-stats">
                          <span title="Température">
                            {planet.current_temperature.toFixed(0)}°C
                          </span>
                          <span title="Gravité">{planet.gravity.toFixed(1)}g</span>
                          <span title="Métal restant">{planet.metal_remaining} Fe</span>
                        </div>
                        {planet.owner_id === mapData.my_player_id && (
                          <div className="planet-details">
                            <div className="population">
                              Pop: {(planet.population / 1000).toFixed(0)}k /{' '}
                              {(planet.max_population / 1000).toFixed(0)}k
                            </div>
                            <div className="budgets">
                              <span>Terra: {planet.terraform_budget}%</span>
                              <span>Mine: {planet.mining_budget}%</span>
                            </div>
                          </div>
                        )}
                      </>
                    )}
                  </div>
                ))}
              </div>

              {/* Fleets at this star */}
              {mapData.fleets.filter((f) => f.current_star_id === selectedStar.id)
                .length > 0 && (
                <>
                  <h3>Flottes</h3>
                  <div className="fleets-list">
                    {mapData.fleets
                      .filter((f) => f.current_star_id === selectedStar.id)
                      .map((fleet) => (
                        <div
                          key={fleet.id}
                          className={`fleet-card ${fleet.player_id === mapData.my_player_id ? 'owned' : ''} ${fleet.id === selectedFleetId ? 'selected' : ''}`}
                          onClick={() => handleFleetClick(fleet.id)}
                        >
                          <span
                            className="fleet-color"
                            style={{ backgroundColor: getPlayerColor(fleet.player_id) }}
                          />
                          <span className="fleet-name">{fleet.name}</span>
                          <span className="fleet-count">{fleet.ship_count} vx</span>
                        </div>
                      ))}
                  </div>
                </>
              )}
            </div>
          ) : (
            <div className="no-selection">
              <p>Cliquez sur une étoile pour voir ses détails</p>
              <div className="help-tips">
                <p><strong>Contrôles:</strong></p>
                <ul>
                  <li>Molette: Zoom</li>
                  <li>Clic + Glisser: Déplacer</li>
                  <li>G/R/S: Niveaux de zoom</li>
                </ul>
              </div>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}

export default GameView;
