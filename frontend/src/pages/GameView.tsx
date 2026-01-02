import { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { GalaxyMap, PlanetPanel, FleetPanel } from '../components/game';
import { PixelUser, PixelLogout, PixelChevron } from '../components/PixelIcons';
import type { Fleet, Player, Galaxy, Planet } from '../hooks/useGameState';
import './GameView.css';

interface GameMapData {
  game_id: number;
  turn: number;
  my_player_id: number;
  galaxy: Galaxy;
  planets: Planet[];
  fleets: Fleet[];
  players: Player[];
}

interface PlayerEconomy {
  money: number;
  metal: number;
  debt: number;
  income: number;
}

function GameView() {
  const { gameId } = useParams<{ gameId: string }>();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const [mapData, setMapData] = useState<GameMapData | null>(null);
  const [economy, setEconomy] = useState<PlayerEconomy | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPlanetId, setSelectedPlanetId] = useState<number | null>(null);
  const [selectedFleetId, setSelectedFleetId] = useState<number | null>(null);
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

  const loadEconomy = useCallback(async () => {
    if (!gameId) return;
    try {
      const data = await api.getEconomy(parseInt(gameId));
      setEconomy(data);
    } catch (err) {
      console.error('Erreur chargement économie:', err);
    }
  }, [gameId]);

  useEffect(() => {
    loadMap();
    loadEconomy();
  }, [loadMap, loadEconomy]);

  const handlePlanetClick = (planetId: number) => {
    setSelectedPlanetId(planetId === selectedPlanetId ? null : planetId);
    setSelectedFleetId(null);
  };

  const handleFleetClick = (fleetId: number) => {
    setSelectedFleetId(fleetId === selectedFleetId ? null : fleetId);
  };

  const handleMoveFleet = async (fleetId: number, destinationPlanetId: number) => {
    try {
      await api.moveFleet(fleetId, destinationPlanetId);
      loadMap();
    } catch (err) {
      console.error('Erreur déplacement flotte:', err);
      const errorMessage =
        (err as { response?: { data?: { error?: string } } })?.response?.data?.error ||
        'Erreur de déplacement';
      alert(errorMessage);
    }
  };

  const getPlayerColor = (playerId: number | null): string => {
    if (!playerId || !mapData) return '#666';
    const player = mapData.players.find((p) => p.id === playerId);
    return player?.color || '#666';
  };

  const getPlayerName = (playerId: number | null): string | undefined => {
    if (!playerId || !mapData) return undefined;
    const player = mapData.players.find((p) => p.id === playerId);
    return player?.player_name;
  };

  const selectedPlanet = mapData?.planets.find((p) => p.id === selectedPlanetId);
  const selectedFleet = mapData?.fleets.find((f) => f.id === selectedFleetId);
  const fleetsAtSelectedPlanet =
    mapData?.fleets.filter((f) => f.current_planet_id === selectedPlanetId) || [];
  const myFleets = mapData?.fleets.filter((f) => f.player_id === mapData.my_player_id) || [];

  // Current player info
  const myPlayer = mapData?.players.find((p) => p.id === mapData.my_player_id);

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
    <div className="game-view spaceward-layout">
      {/* ============ HEADER ============ */}
      <header className="game-header">
        <div className="header-left">
          <div className="header-logo" onClick={() => navigate('/games')}>
            <img src="/game-logo.jpg" alt="Colonie-IA" className="header-logo-img" />
            <span className="header-logo-text">Colonie-IA</span>
          </div>
          <span className="header-separator">|</span>
          <button className="btn-back" onClick={() => navigate('/games')}>
            Quitter
          </button>
          <span className="turn-label">Tour {mapData.turn}</span>
        </div>
        <div className="header-right">
          <button
            className="btn-debug"
            onClick={async () => {
              if (gameId) {
                await api.debugConquerAll(parseInt(gameId));
                loadMap();
              }
            }}
            title="[DEBUG] Conquérir toutes les planètes"
          >
            Conquérir tout
          </button>
          <button className="btn-refresh" onClick={() => { loadMap(); loadEconomy(); }}>
            Actualiser
          </button>
          <button className="btn-end-turn">Fin de tour</button>
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
      </header>

      {/* ============ MAIN AREA ============ */}
      <div className="main-area">
        {/* -------- LEFT PANEL -------- */}
        <aside className="left-panel">
          {/* Planet Info Section */}
          <section className="panel-section planet-info-section">
            {selectedPlanet ? (
              <PlanetPanel
                planet={selectedPlanet}
                isOwned={selectedPlanet.owner_id === mapData.my_player_id}
                ownerColor={getPlayerColor(selectedPlanet.owner_id)}
                ownerName={getPlayerName(selectedPlanet.owner_id)}
                onClose={() => setSelectedPlanetId(null)}
                onBudgetChange={() => { loadMap(); loadEconomy(); }}
                onAbandon={() => {
                  setSelectedPlanetId(null);
                  loadMap();
                  loadEconomy();
                }}
              />
            ) : (
              <div className="no-planet-selected">
                <p className="hint-text">Cliquez sur une planète</p>
              </div>
            )}
          </section>

          {/* Fleet Info Section */}
          {selectedPlanet && fleetsAtSelectedPlanet.length > 0 && (
            <section className="panel-section fleet-info-section">
              <h3>Flottes en orbite</h3>
              <div className="fleet-list-compact">
                {fleetsAtSelectedPlanet.map((fleet) => (
                  <div
                    key={fleet.id}
                    className={`fleet-item ${fleet.player_id === mapData.my_player_id ? 'mine' : ''} ${fleet.id === selectedFleetId ? 'selected' : ''}`}
                    onClick={() => handleFleetClick(fleet.id)}
                  >
                    <span
                      className="fleet-dot"
                      style={{ backgroundColor: getPlayerColor(fleet.player_id) }}
                    />
                    <span className="fleet-name">{fleet.name}</span>
                    <span className="fleet-ships">{fleet.ship_count} vx</span>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Global Resources Section */}
          <section className="panel-section resources-section">
            <h3>Ressources</h3>
            <div className="resource-grid">
              <div className="resource-item">
                <span className="resource-label">Réserve Métal</span>
                <span className="resource-value metal">{economy?.metal?.toLocaleString() || 0}</span>
              </div>
              <div className="resource-item">
                <span className="resource-label">Argent Total</span>
                <span className="resource-value money">${economy?.money?.toLocaleString() || 0}</span>
              </div>
              <div className="resource-item">
                <span className="resource-label">Revenu Total</span>
                <span className="resource-value income">${economy?.income?.toLocaleString() || 0}</span>
              </div>
              {economy && economy.debt > 0 && (
                <div className="resource-item">
                  <span className="resource-label">Dette</span>
                  <span className="resource-value debt">-${economy.debt.toLocaleString()}</span>
                </div>
              )}
            </div>
          </section>
        </aside>

        {/* -------- GALAXY MAP (CENTER) -------- */}
        <main className="map-area">
          <GalaxyMap
            width={mapData.galaxy.width}
            height={mapData.galaxy.height}
            planets={mapData.planets}
            fleets={mapData.fleets}
            players={mapData.players}
            myPlayerId={mapData.my_player_id}
            currentTurn={mapData.turn}
            selectedPlanetId={selectedPlanetId}
            onPlanetClick={handlePlanetClick}
            onFleetClick={handleFleetClick}
            onMoveFleet={handleMoveFleet}
          />
        </main>
      </div>

      {/* ============ BOTTOM BAR ============ */}
      <footer className="bottom-bar">
        {/* Tech Spending Panel */}
        <section className="bottom-panel tech-panel">
          <h4>Dépenses Tech</h4>
          <div className="tech-bars-vertical">
            <div className="tech-bar-v" title="Portée: 40%">
              <span className="tech-bar-value">6</span>
              <div className="tech-fill-v" style={{ height: '40%' }}></div>
              <span className="tech-bar-label">Portée</span>
            </div>
            <div className="tech-bar-v" title="Vitesse: 20%">
              <span className="tech-bar-value">2</span>
              <div className="tech-fill-v" style={{ height: '20%' }}></div>
              <span className="tech-bar-label">Vitesse</span>
            </div>
            <div className="tech-bar-v" title="Armes: 20%">
              <span className="tech-bar-value">2</span>
              <div className="tech-fill-v" style={{ height: '20%' }}></div>
              <span className="tech-bar-label">Armes</span>
            </div>
            <div className="tech-bar-v" title="Boucliers: 15%">
              <span className="tech-bar-value">2</span>
              <div className="tech-fill-v" style={{ height: '15%' }}></div>
              <span className="tech-bar-label">Bouclier</span>
            </div>
            <div className="tech-bar-v" title="Miniaturisation: 5%">
              <span className="tech-bar-value">0</span>
              <div className="tech-fill-v" style={{ height: '5%' }}></div>
              <span className="tech-bar-label">Miniatur.</span>
            </div>
          </div>
        </section>

        {/* Reports Panel */}
        <section className="bottom-panel reports-panel">
          <h4>Rapports</h4>
          <div className="reports-list">
            <div className="report-item">
              <span className="report-icon">📅</span>
              <span className="report-text">Tour {mapData.turn} commencé</span>
            </div>
            {myFleets.filter(f => f.status === 'in_transit').map(fleet => (
              <div key={fleet.id} className="report-item">
                <span className="report-icon">🚀</span>
                <span className="report-text">{fleet.name} en transit (arrivée T{fleet.arrival_turn})</span>
              </div>
            ))}
          </div>
        </section>
      </footer>
    </div>
  );
}

export default GameView;
