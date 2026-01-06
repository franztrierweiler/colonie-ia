import { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import type { RadicalBreakthrough, BreakthroughEffect } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { GalaxyMap, PlanetPanel, TechPanel, TechComparisonModal, BreakthroughModal, BudgetBars } from '../components/game';
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

  // Menus header
  const [shipsMenuOpen, setShipsMenuOpen] = useState(false);
  const [galaxyMenuOpen, setGalaxyMenuOpen] = useState(false);
  const shipsMenuRef = useRef<HTMLDivElement>(null);
  const galaxyMenuRef = useRef<HTMLDivElement>(null);
  const [showFleetsModal, setShowFleetsModal] = useState(false);
  const [showPlanetsModal, setShowPlanetsModal] = useState(false);

  // Technology & Breakthrough state
  const [pendingBreakthrough, setPendingBreakthrough] = useState<RadicalBreakthrough | null>(null);
  const [showBreakthroughModal, setShowBreakthroughModal] = useState(false);
  const [showTechComparison, setShowTechComparison] = useState(false);

  // Turn submission state
  const [isSubmittingTurn, setIsSubmittingTurn] = useState(false);

  // Fleet movement mode - when a fleet is selected for sending
  const [fleetToSend, setFleetToSend] = useState<number | null>(null);

  // Close dropdowns when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
      }
      if (shipsMenuRef.current && !shipsMenuRef.current.contains(event.target as Node)) {
        setShipsMenuOpen(false);
      }
      if (galaxyMenuRef.current && !galaxyMenuRef.current.contains(event.target as Node)) {
        setGalaxyMenuOpen(false);
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

  const loadBreakthroughs = useCallback(async () => {
    if (!gameId) return;
    try {
      const data = await api.getPendingBreakthroughs(parseInt(gameId));
      if (data.pending && data.pending.length > 0) {
        setPendingBreakthrough(data.pending[0]);
        setShowBreakthroughModal(true);
      }
    } catch (err) {
      console.error('Erreur chargement percées:', err);
    }
  }, [gameId]);

  useEffect(() => {
    loadMap();
    loadEconomy();
    loadBreakthroughs();
  }, [loadMap, loadEconomy, loadBreakthroughs]);

  const handlePlanetClick = async (planetId: number) => {
    // If we're in "send fleet" mode, move the fleet to this planet
    if (fleetToSend) {
      const fleet = mapData?.fleets.find(f => f.id === fleetToSend);
      if (fleet && fleet.current_planet_id !== planetId) {
        await handleMoveFleet(fleetToSend, planetId);
      }
      setFleetToSend(null);
      return;
    }

    setSelectedPlanetId(planetId === selectedPlanetId ? null : planetId);
    setSelectedFleetId(null);
  };

  const handleSendFleet = (fleetId: number) => {
    setFleetToSend(fleetId);
  };

  const cancelSendFleet = () => {
    setFleetToSend(null);
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

  const handleSendShips = async (
    originPlanetId: number,
    destinationPlanetId: number,
    shipsToSend: Record<string, number>
  ) => {
    try {
      await api.sendShipsFromPlanet(originPlanetId, destinationPlanetId, shipsToSend);
      await loadMap();
    } catch (err) {
      console.error('Erreur envoi vaisseaux:', err);
      const errorMessage =
        (err as { response?: { data?: { error?: string } } })?.response?.data?.error ||
        'Erreur d\'envoi des vaisseaux';
      alert(errorMessage);
    }
  };

  const handleSubmitTurn = async () => {
    if (!gameId || isSubmittingTurn) return;

    setIsSubmittingTurn(true);
    try {
      const result = await api.submitTurn(parseInt(gameId));

      if (result.turn_processed) {
        // Turn was processed - reload all data
        await Promise.all([loadMap(), loadEconomy(), loadBreakthroughs()]);
      }
    } catch (err) {
      console.error('Erreur soumission tour:', err);
      const errorMessage =
        (err as { response?: { data?: { error?: string } } })?.response?.data?.error ||
        'Erreur de soumission du tour';
      alert(errorMessage);
    } finally {
      setIsSubmittingTurn(false);
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
          {/* Menu Vaisseaux */}
          <div className="header-menu" ref={shipsMenuRef}>
            <button
              className="btn-header-menu"
              onClick={() => { setShipsMenuOpen(!shipsMenuOpen); setGalaxyMenuOpen(false); }}
            >
              Vaisseaux
              <PixelChevron
                className={`menu-arrow ${shipsMenuOpen ? 'open' : ''}`}
                size={10}
                direction={shipsMenuOpen ? 'up' : 'down'}
              />
            </button>
            {shipsMenuOpen && (
              <div className="header-menu-dropdown">
                <button
                  className="header-menu-item"
                  onClick={() => { setShowFleetsModal(true); setShipsMenuOpen(false); }}
                >
                  Afficher tout
                </button>
                <button
                  className="header-menu-item"
                  onClick={() => {
                    setShipsMenuOpen(false);
                    // Scroll to ships section in planet panel
                    document.querySelector('.ships-section-compact')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
                  }}
                  disabled={!selectedPlanetId || !selectedPlanet || selectedPlanet.owner_id !== mapData.my_player_id}
                >
                  Créer sur la planète
                </button>
              </div>
            )}
          </div>
          {/* Menu Galaxie */}
          <div className="header-menu" ref={galaxyMenuRef}>
            <button
              className="btn-header-menu"
              onClick={() => { setGalaxyMenuOpen(!galaxyMenuOpen); setShipsMenuOpen(false); }}
            >
              Galaxie
              <PixelChevron
                className={`menu-arrow ${galaxyMenuOpen ? 'open' : ''}`}
                size={10}
                direction={galaxyMenuOpen ? 'up' : 'down'}
              />
            </button>
            {galaxyMenuOpen && (
              <div className="header-menu-dropdown">
                <button
                  className="header-menu-item"
                  onClick={() => { setShowPlanetsModal(true); setGalaxyMenuOpen(false); }}
                >
                  Mes planètes
                </button>
              </div>
            )}
          </div>
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
          <button
            className="btn-end-turn"
            onClick={handleSubmitTurn}
            disabled={isSubmittingTurn}
          >
            {isSubmittingTurn ? 'Traitement...' : 'Fin de tour'}
          </button>
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
                fleets={fleetsAtSelectedPlanet}
                myPlayerId={mapData.my_player_id}
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

          {/* Global Resources Section */}
          <section className="panel-section resources-section">
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

          {/* Budget Allocation Bars */}
          <section className="panel-section budget-bars-section">
            <BudgetBars
              gameId={parseInt(gameId || '0')}
              planets={mapData.planets.filter(p => p.owner_id === mapData.my_player_id)}
              playerColor={myPlayer?.color || '#ffa500'}
              economy={economy}
              onPlanetClick={(planetId) => setSelectedPlanetId(planetId)}
              selectedPlanetId={selectedPlanetId}
            />
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
            selectedFleetId={selectedFleetId}
            onPlanetClick={handlePlanetClick}
            onFleetClick={handleFleetClick}
            onMoveFleet={handleMoveFleet}
            onSendShips={handleSendShips}
          />
        </main>
      </div>

      {/* ============ BOTTOM BAR ============ */}
      <footer className="bottom-bar">
        {/* Tech Panel - Real component */}
        <TechPanel
          gameId={parseInt(gameId || '0')}
          onBreakthroughClick={(breakthrough) => {
            setPendingBreakthrough(breakthrough);
            setShowBreakthroughModal(true);
          }}
          onComparisonClick={() => setShowTechComparison(true)}
        />

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

      {/* ============ MODALS ============ */}
      {/* Breakthrough Modal */}
      {pendingBreakthrough && (
        <BreakthroughModal
          breakthrough={pendingBreakthrough}
          isOpen={showBreakthroughModal}
          onClose={() => setShowBreakthroughModal(false)}
          onResolved={() => {
            setShowBreakthroughModal(false);
            setPendingBreakthrough(null);
            loadBreakthroughs();
          }}
        />
      )}

      {/* Tech Comparison Modal */}
      <TechComparisonModal
        gameId={parseInt(gameId || '0')}
        isOpen={showTechComparison}
        onClose={() => setShowTechComparison(false)}
      />

      {/* Fleets Modal */}
      {showFleetsModal && (
        <div className="expert-modal-overlay" onClick={() => setShowFleetsModal(false)}>
          <div className="expert-modal" onClick={(e) => e.stopPropagation()}>
            <div className="expert-modal-header">
              <span>Flottes ({myFleets.length})</span>
              <button onClick={() => setShowFleetsModal(false)}>×</button>
            </div>
            <div className="expert-modal-content">
              <table className="expert-table">
                <thead>
                  <tr>
                    <th>Nom</th>
                    <th>Position</th>
                    <th>Vx</th>
                    <th>Statut</th>
                  </tr>
                </thead>
                <tbody>
                  {myFleets.map((fleet) => {
                    const planet = mapData?.planets.find(p => p.id === fleet.current_planet_id);
                    const destPlanet = mapData?.planets.find(p => p.id === fleet.destination_planet_id);
                    return (
                      <tr key={fleet.id} onClick={() => {
                        if (fleet.current_planet_id) {
                          setSelectedPlanetId(fleet.current_planet_id);
                        }
                        setShowFleetsModal(false);
                      }}>
                        <td>{fleet.name}</td>
                        <td>{planet?.name || '—'}</td>
                        <td>{fleet.ship_count}</td>
                        <td>{fleet.status === 'stationed' ? 'Stationné' : `→ ${destPlanet?.name || '?'}`}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Planets Modal */}
      {showPlanetsModal && (
        <div className="expert-modal-overlay" onClick={() => setShowPlanetsModal(false)}>
          <div className="expert-modal" onClick={(e) => e.stopPropagation()}>
            <div className="expert-modal-header">
              <span>Mes planètes ({mapData?.planets.filter(p => p.owner_id === mapData.my_player_id).length})</span>
              <button onClick={() => setShowPlanetsModal(false)}>×</button>
            </div>
            <div className="expert-modal-content">
              <table className="expert-table">
                <thead>
                  <tr>
                    <th>Nom</th>
                    <th>Pop</th>
                    <th>Métal</th>
                    <th>T/M/V</th>
                  </tr>
                </thead>
                <tbody>
                  {mapData?.planets
                    .filter(p => p.owner_id === mapData.my_player_id)
                    .sort((a, b) => b.population - a.population)
                    .map((planet) => (
                      <tr key={planet.id} onClick={() => {
                        setSelectedPlanetId(planet.id);
                        setShowPlanetsModal(false);
                      }}>
                        <td>{planet.name}</td>
                        <td>{(planet.population / 1000).toFixed(0)}k</td>
                        <td>{planet.metal_remaining.toLocaleString()}</td>
                        <td>{planet.terraform_budget}/{planet.mining_budget}/{planet.ships_budget}</td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default GameView;
