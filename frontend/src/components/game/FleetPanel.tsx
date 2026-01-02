import { useState, useEffect } from 'react';
import type { Fleet, Planet, ShipDesign } from '../../hooks/useGameState';
import { SHIP_TYPES } from '../../hooks/useGameState';
import api from '../../services/api';
import './FleetPanel.css';

interface FleetPanelProps {
  gameId: number;
  fleets: Fleet[];
  planets: Planet[];
  myPlayerId: number;
  selectedFleetId: number | null;
  onSelectFleet: (fleetId: number | null) => void;
  onFleetAction: () => void;
}

function FleetPanel({
  gameId,
  fleets,
  planets,
  myPlayerId,
  selectedFleetId,
  onSelectFleet,
  onFleetAction,
}: FleetPanelProps) {
  const [designs, setDesigns] = useState<ShipDesign[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showDesigner, setShowDesigner] = useState(false);
  const [showBuildModal, setShowBuildModal] = useState(false);
  const [selectedDesignId, setSelectedDesignId] = useState<number | null>(null);

  const myFleets = fleets.filter((f) => f.player_id === myPlayerId);
  const selectedFleet = myFleets.find((f) => f.id === selectedFleetId);

  // Charger les designs
  useEffect(() => {
    const loadDesigns = async () => {
      try {
        const data = await api.getDesigns(gameId);
        setDesigns(data.designs || []);
      } catch (err) {
        console.error('Erreur chargement designs:', err);
      }
    };
    loadDesigns();
  }, [gameId]);

  const getPlanetName = (planetId: number | null): string => {
    if (!planetId) return 'Espace';
    const planet = planets.find((p) => p.id === planetId);
    return planet?.name || 'Inconnu';
  };

  const getStatusLabel = (fleet: Fleet): string => {
    if (fleet.status === 'in_transit') {
      return `En route vers ${getPlanetName(fleet.destination_planet_id)}`;
    }
    if (fleet.status === 'arriving') {
      return `Arrive sur ${getPlanetName(fleet.destination_planet_id)}`;
    }
    return `En orbite de ${getPlanetName(fleet.current_planet_id)}`;
  };

  const handleDisband = async () => {
    if (!selectedFleet) return;
    if (!window.confirm(`Voulez-vous vraiment démanteler la flotte "${selectedFleet.name}" ? Vous récupérerez 75% du métal.`)) {
      return;
    }
    setIsLoading(true);
    try {
      const result = await api.disbandFleet(selectedFleet.id);
      alert(`Flotte démantelée ! Métal récupéré : ${result.metal_recovered}`);
      onSelectFleet(null);
      onFleetAction();
    } catch (err) {
      console.error('Erreur démantèlement:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateFleet = async () => {
    const name = window.prompt('Nom de la nouvelle flotte :');
    if (!name) return;

    // Trouver une planète possédée pour créer la flotte
    const myPlanet = planets.find((p) => p.owner_id === myPlayerId);
    if (!myPlanet) {
      alert('Vous devez posséder une planète pour créer une flotte.');
      return;
    }

    setIsLoading(true);
    try {
      await api.createFleet(gameId, name, myPlanet.id);
      onFleetAction();
    } catch (err) {
      console.error('Erreur création flotte:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fleet-panel">
      <div className="panel-header">
        <h2>Flottes</h2>
        <button className="btn-small" onClick={handleCreateFleet} disabled={isLoading}>
          + Nouvelle
        </button>
      </div>

      {/* Liste des flottes */}
      <div className="fleet-list">
        {myFleets.length === 0 ? (
          <p className="no-fleets">Aucune flotte</p>
        ) : (
          myFleets.map((fleet) => (
            <div
              key={fleet.id}
              className={`fleet-item ${selectedFleetId === fleet.id ? 'selected' : ''}`}
              onClick={() => onSelectFleet(fleet.id === selectedFleetId ? null : fleet.id)}
            >
              <div className="fleet-item-header">
                <span className="fleet-name">{fleet.name}</span>
                <span className="fleet-count">{fleet.ship_count} vaisseaux</span>
              </div>
              <div className="fleet-item-status">
                {fleet.status === 'in_transit' && <span className="status-badge transit">En transit</span>}
                {fleet.status === 'stationed' && <span className="status-badge stationed">En orbite</span>}
                <span className="fleet-location">{getPlanetName(fleet.current_planet_id || fleet.destination_planet_id)}</span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Détails de la flotte sélectionnée */}
      {selectedFleet && (
        <div className="fleet-details">
          <h3>{selectedFleet.name}</h3>
          <p className="fleet-status">{getStatusLabel(selectedFleet)}</p>

          {/* Statistiques */}
          <div className="fleet-stats">
            <div className="stat">
              <span className="stat-label">Vitesse</span>
              <span className="stat-value">{selectedFleet.fleet_speed.toFixed(1)}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Portée</span>
              <span className="stat-value">{selectedFleet.fleet_range.toFixed(1)}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Armes</span>
              <span className="stat-value">{selectedFleet.total_weapons.toFixed(1)}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Boucliers</span>
              <span className="stat-value">{selectedFleet.total_shields.toFixed(1)}</span>
            </div>
          </div>

          {/* Carburant */}
          <div className="fuel-bar-container">
            <span className="fuel-label">Carburant</span>
            <div className="fuel-bar">
              <div
                className="fuel-fill"
                style={{ width: `${(selectedFleet.fuel_remaining / selectedFleet.max_fuel) * 100}%` }}
              />
            </div>
            <span className="fuel-value">
              {selectedFleet.fuel_remaining.toFixed(0)} / {selectedFleet.max_fuel.toFixed(0)}
            </span>
          </div>

          {/* Vaisseaux par type */}
          <div className="ships-by-type">
            <h4>Composition</h4>
            {Object.entries(selectedFleet.ships_by_type).map(([type, count]) => {
              const shipInfo = SHIP_TYPES[type as keyof typeof SHIP_TYPES];
              return (
                <div key={type} className="ship-type-row">
                  <span className="ship-icon">{shipInfo?.icon || '?'}</span>
                  <span className="ship-type-name">{shipInfo?.name || type}</span>
                  <span className="ship-type-count">x{count}</span>
                </div>
              );
            })}
            {Object.keys(selectedFleet.ships_by_type).length === 0 && (
              <p className="no-ships">Aucun vaisseau</p>
            )}
          </div>

          {/* Actions */}
          <div className="fleet-actions">
            {selectedFleet.status === 'stationed' && (
              <>
                <button
                  className="btn-secondary"
                  onClick={() => setShowBuildModal(true)}
                  disabled={isLoading}
                >
                  Construire
                </button>
                <button
                  className="btn-danger"
                  onClick={handleDisband}
                  disabled={isLoading || selectedFleet.ship_count === 0}
                >
                  Démanteler
                </button>
              </>
            )}
            {selectedFleet.status === 'in_transit' && selectedFleet.arrival_turn && (
              <p className="arrival-info">Arrivée au tour {selectedFleet.arrival_turn}</p>
            )}
          </div>
        </div>
      )}

      {/* Designs de vaisseaux */}
      <div className="designs-section">
        <div className="section-header">
          <h3>Designs</h3>
          <button className="btn-small" onClick={() => setShowDesigner(true)}>
            + Nouveau
          </button>
        </div>
        <div className="designs-list">
          {designs.map((design) => {
            const shipInfo = SHIP_TYPES[design.ship_type as keyof typeof SHIP_TYPES];
            return (
              <div
                key={design.id}
                className={`design-item ${selectedDesignId === design.id ? 'selected' : ''}`}
                onClick={() => setSelectedDesignId(design.id === selectedDesignId ? null : design.id)}
              >
                <span className="design-icon">{shipInfo?.icon || '?'}</span>
                <div className="design-info">
                  <span className="design-name">{design.name}</span>
                  <span className="design-type">{shipInfo?.name || design.ship_type}</span>
                </div>
                <div className="design-cost">
                  <span>{design.production_cost_metal}M</span>
                  <span>{design.production_cost_money}$</span>
                </div>
              </div>
            );
          })}
          {designs.length === 0 && <p className="no-designs">Aucun design</p>}
        </div>
      </div>

      {/* Modal de construction simple */}
      {showBuildModal && selectedFleet && (
        <BuildShipModal
          gameId={gameId}
          fleetId={selectedFleet.id}
          designs={designs}
          onClose={() => setShowBuildModal(false)}
          onBuild={onFleetAction}
        />
      )}

      {/* Modal de conception */}
      {showDesigner && (
        <ShipDesignerModal
          gameId={gameId}
          onClose={() => setShowDesigner(false)}
          onCreated={() => {
            setShowDesigner(false);
            // Recharger les designs
            api.getDesigns(gameId).then((data) => setDesigns(data.designs || []));
          }}
        />
      )}
    </div>
  );
}

// =============================================================================
// Sous-composant : Modal de construction
// =============================================================================

interface BuildShipModalProps {
  gameId: number;
  fleetId: number;
  designs: ShipDesign[];
  onClose: () => void;
  onBuild: () => void;
}

function BuildShipModal({ gameId, fleetId, designs, onClose, onBuild }: BuildShipModalProps) {
  const [selectedDesignId, setSelectedDesignId] = useState<number | null>(null);
  const [count, setCount] = useState(1);
  const [isBuilding, setIsBuilding] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedDesign = designs.find((d) => d.id === selectedDesignId);

  const handleBuild = async () => {
    if (!selectedDesignId) return;

    setIsBuilding(true);
    setError(null);

    try {
      await api.buildShips(gameId, selectedDesignId, fleetId, count);
      onBuild();
      onClose();
    } catch (err: unknown) {
      const error = err as { response?: { data?: { error?: string } } };
      setError(error.response?.data?.error || 'Erreur de construction');
    } finally {
      setIsBuilding(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <h3>Construire des vaisseaux</h3>

        <div className="build-designs">
          {designs.map((design) => {
            const shipInfo = SHIP_TYPES[design.ship_type as keyof typeof SHIP_TYPES];
            const costLabel = design.is_prototype_built
              ? `${design.production_cost_metal}M / ${design.production_cost_money}$`
              : `${design.prototype_cost_metal}M / ${design.prototype_cost_money}$ (prototype)`;

            return (
              <div
                key={design.id}
                className={`build-design-item ${selectedDesignId === design.id ? 'selected' : ''}`}
                onClick={() => setSelectedDesignId(design.id)}
              >
                <span className="design-icon">{shipInfo?.icon || '?'}</span>
                <div className="design-info">
                  <span className="design-name">{design.name}</span>
                  <span className="design-cost">{costLabel}</span>
                </div>
              </div>
            );
          })}
        </div>

        {selectedDesign && (
          <div className="build-count">
            <label>Quantité :</label>
            <input
              type="number"
              min="1"
              max="100"
              value={count}
              onChange={(e) => setCount(Math.max(1, parseInt(e.target.value) || 1))}
            />
            <span className="total-cost">
              Total : {(selectedDesign.is_prototype_built ? selectedDesign.production_cost_metal : selectedDesign.prototype_cost_metal) * count}M /
              {(selectedDesign.is_prototype_built ? selectedDesign.production_cost_money : selectedDesign.prototype_cost_money) * count}$
            </span>
          </div>
        )}

        {error && <p className="error-message">{error}</p>}

        <div className="modal-actions">
          <button className="btn-secondary" onClick={onClose} disabled={isBuilding}>
            Annuler
          </button>
          <button
            className="btn-primary"
            onClick={handleBuild}
            disabled={!selectedDesignId || isBuilding}
          >
            {isBuilding ? 'Construction...' : 'Construire'}
          </button>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Sous-composant : Modal de conception
// =============================================================================

interface ShipDesignerModalProps {
  gameId: number;
  onClose: () => void;
  onCreated: () => void;
}

function ShipDesignerModal({ gameId, onClose, onCreated }: ShipDesignerModalProps) {
  const [name, setName] = useState('');
  const [shipType, setShipType] = useState('fighter');
  const [rangeLevel, setRangeLevel] = useState(1);
  const [speedLevel, setSpeedLevel] = useState(1);
  const [weaponsLevel, setWeaponsLevel] = useState(1);
  const [shieldsLevel, setShieldsLevel] = useState(1);
  const [miniLevel, setMiniLevel] = useState(1);
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCreate = async () => {
    if (!name.trim()) {
      setError('Le nom est requis');
      return;
    }

    setIsCreating(true);
    setError(null);

    try {
      await api.createDesign(gameId, {
        name: name.trim(),
        ship_type: shipType,
        range_level: rangeLevel,
        speed_level: speedLevel,
        weapons_level: weaponsLevel,
        shields_level: shieldsLevel,
        mini_level: miniLevel,
      });
      onCreated();
    } catch (err: unknown) {
      const error = err as { response?: { data?: { error?: string } } };
      setError(error.response?.data?.error || 'Erreur de création');
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content designer-modal" onClick={(e) => e.stopPropagation()}>
        <h3>Nouveau design de vaisseau</h3>

        <div className="design-form">
          <div className="form-group">
            <label>Nom du design</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Ex: Chasseur Mk.I"
            />
          </div>

          <div className="form-group">
            <label>Type de vaisseau</label>
            <select value={shipType} onChange={(e) => setShipType(e.target.value)}>
              {Object.entries(SHIP_TYPES).map(([type, info]) => (
                <option key={type} value={type}>
                  {info.icon} {info.name}
                </option>
              ))}
            </select>
          </div>

          <div className="tech-sliders">
            <div className="slider-group">
              <label>Portée : {rangeLevel}</label>
              <input
                type="range"
                min="1"
                max="10"
                value={rangeLevel}
                onChange={(e) => setRangeLevel(parseInt(e.target.value))}
              />
            </div>
            <div className="slider-group">
              <label>Vitesse : {speedLevel}</label>
              <input
                type="range"
                min="1"
                max="10"
                value={speedLevel}
                onChange={(e) => setSpeedLevel(parseInt(e.target.value))}
              />
            </div>
            <div className="slider-group">
              <label>Armes : {weaponsLevel}</label>
              <input
                type="range"
                min="1"
                max="10"
                value={weaponsLevel}
                onChange={(e) => setWeaponsLevel(parseInt(e.target.value))}
              />
            </div>
            <div className="slider-group">
              <label>Boucliers : {shieldsLevel}</label>
              <input
                type="range"
                min="1"
                max="10"
                value={shieldsLevel}
                onChange={(e) => setShieldsLevel(parseInt(e.target.value))}
              />
            </div>
            <div className="slider-group">
              <label>Miniaturisation : {miniLevel}</label>
              <input
                type="range"
                min="1"
                max="10"
                value={miniLevel}
                onChange={(e) => setMiniLevel(parseInt(e.target.value))}
              />
            </div>
          </div>
        </div>

        {error && <p className="error-message">{error}</p>}

        <div className="modal-actions">
          <button className="btn-secondary" onClick={onClose} disabled={isCreating}>
            Annuler
          </button>
          <button className="btn-primary" onClick={handleCreate} disabled={isCreating}>
            {isCreating ? 'Création...' : 'Créer le design'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default FleetPanel;
