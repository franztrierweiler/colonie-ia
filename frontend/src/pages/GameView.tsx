import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import './GameView.css';

// Types
interface Planet {
  id: number;
  name: string;
  star_id: number;
  orbit_index: number;
  temperature: number;
  current_temperature: number;
  gravity: number;
  metal_reserves: number;
  metal_remaining: number;
  state: string;
  owner_id: number | null;
  population: number;
  max_population: number;
  habitability: number;
  terraform_budget: number;
  mining_budget: number;
  is_home_planet: boolean;
}

interface Star {
  id: number;
  name: string;
  x: number;
  y: number;
  is_nova: boolean;
  planet_count: number;
  planets: Planet[];
}

interface Fleet {
  id: number;
  name: string;
  player_id: number;
  status: string;
  current_star_id: number | null;
  destination_star_id: number | null;
  ship_count: number;
  fleet_speed: number;
  fleet_range: number;
}

interface Player {
  id: number;
  player_name: string;
  color: string;
  is_ai: boolean;
}

interface Galaxy {
  id: number;
  width: number;
  height: number;
  shape: string;
  star_count: number;
}

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

  // Zoom et pan
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });

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
  };

  const handleZoomIn = () => setZoom((z) => Math.min(z * 1.5, 4));
  const handleZoomOut = () => setZoom((z) => Math.max(z / 1.5, 0.25));
  const handleZoomReset = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  const getPlayerColor = (playerId: number | null): string => {
    if (!playerId || !mapData) return '#666';
    const player = mapData.players.find((p) => p.id === playerId);
    return player?.color || '#666';
  };

  const selectedStar = mapData?.stars.find((s) => s.id === selectedStarId);

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
          <button className="btn-primary">Fin de tour</button>
        </div>
      </header>

      {/* Main content */}
      <div className="game-content">
        {/* Galaxy Map */}
        <div className="galaxy-map-container">
          <div className="zoom-controls">
            <button onClick={handleZoomIn}>+</button>
            <button onClick={handleZoomReset}>1:1</button>
            <button onClick={handleZoomOut}>-</button>
          </div>

          <svg
            className="galaxy-map"
            viewBox={`0 0 ${mapData.galaxy.width} ${mapData.galaxy.height}`}
            style={{
              transform: `scale(${zoom}) translate(${pan.x}px, ${pan.y}px)`,
            }}
          >
            {/* Background */}
            <rect
              x="0"
              y="0"
              width={mapData.galaxy.width}
              height={mapData.galaxy.height}
              fill="#0a0a1a"
            />

            {/* Fleet trajectories */}
            {mapData.fleets
              .filter((f) => f.status === 'in_transit' && f.current_star_id && f.destination_star_id)
              .map((fleet) => {
                const fromStar = mapData.stars.find((s) => s.id === fleet.current_star_id);
                const toStar = mapData.stars.find((s) => s.id === fleet.destination_star_id);
                if (!fromStar || !toStar) return null;
                return (
                  <line
                    key={`trajectory-${fleet.id}`}
                    x1={fromStar.x}
                    y1={fromStar.y}
                    x2={toStar.x}
                    y2={toStar.y}
                    stroke={getPlayerColor(fleet.player_id)}
                    strokeWidth="0.5"
                    strokeDasharray="2,2"
                    opacity="0.6"
                  />
                );
              })}

            {/* Stars */}
            {mapData.stars.map((star) => {
              const hasOwnedPlanet = star.planets.some(
                (p) => p.owner_id === mapData.my_player_id
              );
              const hasEnemyPlanet = star.planets.some(
                (p) => p.owner_id && p.owner_id !== mapData.my_player_id
              );
              const isSelected = star.id === selectedStarId;

              return (
                <g
                  key={star.id}
                  className={`star-group ${isSelected ? 'selected' : ''}`}
                  onClick={() => handleStarClick(star.id)}
                  style={{ cursor: 'pointer' }}
                >
                  {/* Star glow */}
                  <circle
                    cx={star.x}
                    cy={star.y}
                    r={isSelected ? 4 : 3}
                    fill={star.is_nova ? '#ff4444' : '#ffdd44'}
                    opacity="0.3"
                  />
                  {/* Star core */}
                  <circle
                    cx={star.x}
                    cy={star.y}
                    r={isSelected ? 2.5 : 2}
                    fill={star.is_nova ? '#ff0000' : '#ffffff'}
                  />
                  {/* Ownership indicator */}
                  {hasOwnedPlanet && (
                    <circle
                      cx={star.x}
                      cy={star.y}
                      r={5}
                      fill="none"
                      stroke={getPlayerColor(mapData.my_player_id)}
                      strokeWidth="1"
                    />
                  )}
                  {hasEnemyPlanet && !hasOwnedPlanet && (
                    <circle
                      cx={star.x}
                      cy={star.y}
                      r={5}
                      fill="none"
                      stroke="#ff4444"
                      strokeWidth="0.5"
                      strokeDasharray="1,1"
                    />
                  )}
                  {/* Star name (only at higher zoom) */}
                  {zoom >= 1.5 && (
                    <text
                      x={star.x}
                      y={star.y + 8}
                      textAnchor="middle"
                      fill="#aaa"
                      fontSize="3"
                    >
                      {star.name}
                    </text>
                  )}
                </g>
              );
            })}

            {/* Fleet markers */}
            {mapData.fleets
              .filter((f) => f.status === 'stationed' && f.current_star_id)
              .map((fleet) => {
                const star = mapData.stars.find((s) => s.id === fleet.current_star_id);
                if (!star) return null;
                const isMine = fleet.player_id === mapData.my_player_id;
                return (
                  <g key={`fleet-${fleet.id}`}>
                    <polygon
                      points={`${star.x + 4},${star.y - 2} ${star.x + 7},${star.y} ${star.x + 4},${star.y + 2}`}
                      fill={getPlayerColor(fleet.player_id)}
                      stroke={isMine ? '#fff' : 'none'}
                      strokeWidth="0.3"
                    />
                    {zoom >= 1 && (
                      <text
                        x={star.x + 8}
                        y={star.y + 1}
                        fill={getPlayerColor(fleet.player_id)}
                        fontSize="3"
                      >
                        {fleet.ship_count}
                      </text>
                    )}
                  </g>
                );
              })}
          </svg>
        </div>

        {/* Side Panel */}
        <aside className="side-panel">
          {selectedStar ? (
            <div className="star-info">
              <h2>{selectedStar.name}</h2>
              <p className="star-coords">
                Position: ({selectedStar.x.toFixed(1)}, {selectedStar.y.toFixed(1)})
              </p>

              <h3>Planètes ({selectedStar.planets.length})</h3>
              <div className="planets-list">
                {selectedStar.planets.map((planet) => (
                  <div
                    key={planet.id}
                    className={`planet-card ${planet.owner_id === mapData.my_player_id ? 'owned' : ''}`}
                  >
                    <div className="planet-header">
                      <span className="planet-name">{planet.name}</span>
                      {planet.owner_id && (
                        <span
                          className="owner-dot"
                          style={{ backgroundColor: getPlayerColor(planet.owner_id) }}
                        />
                      )}
                    </div>
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
                          Pop: {(planet.population / 1000).toFixed(0)}k / {(planet.max_population / 1000).toFixed(0)}k
                        </div>
                        <div className="budgets">
                          <span>Terra: {planet.terraform_budget}%</span>
                          <span>Mine: {planet.mining_budget}%</span>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* Fleets at this star */}
              {mapData.fleets.filter((f) => f.current_star_id === selectedStar.id).length > 0 && (
                <>
                  <h3>Flottes</h3>
                  <div className="fleets-list">
                    {mapData.fleets
                      .filter((f) => f.current_star_id === selectedStar.id)
                      .map((fleet) => (
                        <div
                          key={fleet.id}
                          className={`fleet-card ${fleet.player_id === mapData.my_player_id ? 'owned' : ''}`}
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
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}

export default GameView;
