import { useState, useCallback, useEffect } from 'react';
import type { Planet, ProductionQueueItem, ShipDesign } from '../../hooks/useGameState';
import api from '../../services/api';
import './PlanetPanel.css';

interface PlanetPanelProps {
  planet: Planet;
  isOwned: boolean;
  ownerColor: string;
  ownerName?: string;
  onClose: () => void;
  onBudgetChange: () => void;
  onAbandon: () => void;
}

function PlanetPanel({
  planet,
  isOwned,
  ownerColor,
  ownerName,
  onClose,
  onBudgetChange,
  onAbandon,
}: PlanetPanelProps) {
  const [terraformBudget, setTerraformBudget] = useState(planet.terraform_budget);
  const [miningBudget, setMiningBudget] = useState(planet.mining_budget);
  const [shipsBudget, setShipsBudget] = useState(planet.ships_budget || 0);
  const [isSaving, setIsSaving] = useState(false);
  const [showAbandonConfirm, setShowAbandonConfirm] = useState(false);
  const [stripMine, setStripMine] = useState(true);
  const [showHistory, setShowHistory] = useState(false);

  // Production queue state
  const [productionQueue, setProductionQueue] = useState<ProductionQueueItem[]>([]);
  const [designs, setDesigns] = useState<ShipDesign[]>([]);
  const [selectedDesign, setSelectedDesign] = useState<number | null>(null);
  const [productionOutput, setProductionOutput] = useState(0);
  const [showAddProduction, setShowAddProduction] = useState(false);

  const hasChanges =
    terraformBudget !== planet.terraform_budget ||
    miningBudget !== planet.mining_budget ||
    shipsBudget !== (planet.ships_budget || 0);

  useEffect(() => {
    if (isOwned) {
      loadProductionQueue();
      loadDesigns();
    }
  }, [isOwned, planet.id]);

  const loadProductionQueue = async () => {
    try {
      const data = await api.getProductionQueue(planet.id);
      setProductionQueue(data.queue || []);
      setProductionOutput(data.production_output_per_turn || 0);
    } catch (err) {
      console.error('Erreur chargement file de production:', err);
    }
  };

  const loadDesigns = async () => {
    try {
      const gamesData = await api.getMyGames();
      if (gamesData.games && gamesData.games.length > 0) {
        const gameId = gamesData.games[0].id;
        const designsData = await api.getDesigns(gameId);
        setDesigns(designsData.designs || []);
      }
    } catch (err) {
      console.error('Erreur chargement designs:', err);
    }
  };

  const handleBudgetBarClick = (type: 'terraform' | 'mining' | 'ships', e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const clickY = e.clientY - rect.top;
    const percentage = Math.round(100 - (clickY / rect.height) * 100);
    const clampedValue = Math.max(0, Math.min(100, percentage));

    handleBudgetChange(type, clampedValue);
  };

  const handleBudgetChange = useCallback(
    (type: 'terraform' | 'mining' | 'ships', value: number) => {
      const total = 100;
      let newTerraform = terraformBudget;
      let newMining = miningBudget;
      let newShips = shipsBudget;

      if (type === 'terraform') {
        newTerraform = value;
        const remaining = total - value;
        const oldOtherSum = miningBudget + shipsBudget;
        if (oldOtherSum > 0) {
          newMining = Math.round((miningBudget / oldOtherSum) * remaining);
          newShips = remaining - newMining;
        } else {
          newMining = Math.round(remaining / 2);
          newShips = remaining - newMining;
        }
      } else if (type === 'mining') {
        newMining = value;
        const remaining = total - value;
        const oldOtherSum = terraformBudget + shipsBudget;
        if (oldOtherSum > 0) {
          newTerraform = Math.round((terraformBudget / oldOtherSum) * remaining);
          newShips = remaining - newTerraform;
        } else {
          newTerraform = Math.round(remaining / 2);
          newShips = remaining - newTerraform;
        }
      } else {
        newShips = value;
        const remaining = total - value;
        const oldOtherSum = terraformBudget + miningBudget;
        if (oldOtherSum > 0) {
          newTerraform = Math.round((terraformBudget / oldOtherSum) * remaining);
          newMining = remaining - newTerraform;
        } else {
          newTerraform = Math.round(remaining / 2);
          newMining = remaining - newTerraform;
        }
      }

      newTerraform = Math.max(0, Math.min(100, newTerraform));
      newMining = Math.max(0, Math.min(100, newMining));
      newShips = Math.max(0, Math.min(100, newShips));

      setTerraformBudget(newTerraform);
      setMiningBudget(newMining);
      setShipsBudget(newShips);
    },
    [terraformBudget, miningBudget, shipsBudget]
  );

  const handleSaveBudget = async () => {
    setIsSaving(true);
    try {
      await api.updatePlanetBudget(planet.id, terraformBudget, miningBudget, shipsBudget);
      onBudgetChange();
    } catch (err) {
      console.error('Erreur lors de la sauvegarde du budget:', err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleAbandon = async () => {
    setIsSaving(true);
    try {
      await api.abandonPlanet(planet.id, stripMine);
      setShowAbandonConfirm(false);
      onAbandon();
    } catch (err) {
      console.error("Erreur lors de l'abandon:", err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddToQueue = async () => {
    if (!selectedDesign) return;
    setIsSaving(true);
    try {
      await api.addToProductionQueue(planet.id, selectedDesign);
      await loadProductionQueue();
      setShowAddProduction(false);
      setSelectedDesign(null);
    } catch (err) {
      console.error('Erreur ajout à la file:', err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleRemoveFromQueue = async (queueId: number) => {
    try {
      await api.removeFromProductionQueue(queueId);
      await loadProductionQueue();
    } catch (err) {
      console.error('Erreur suppression de la file:', err);
    }
  };

  // Calcul revenu estimé
  const estimatedIncome = planet.population > 0
    ? Math.round(planet.population * planet.habitability * 0.1)
    : 0;

  return (
    <div className="planet-panel compact">
      {/* Header avec nom et barres budget */}
      <div className="panel-header-compact">
        <div className="planet-info-left">
          <div className="planet-name-row">
            <h2>{planet.name}</h2>
            {planet.is_home_planet && <span className="home-badge">★</span>}
            {planet.state !== 'unexplored' && (planet.history_line1 || planet.history_line2) && (
              <button
                className="btn-history"
                onClick={() => setShowHistory(true)}
                title="Histoire de la planète"
              >
                📖
              </button>
            )}
            <button className="close-btn" onClick={onClose}>×</button>
          </div>

          {/* Stats compactes style Spaceward Ho! */}
          <div className="stats-compact">
            <div className="stat-row">
              <span className="stat-label">Revenu:</span>
              <span className="stat-value">${estimatedIncome.toLocaleString()}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Pop:</span>
              <span className="stat-value">{(planet.population / 1000).toFixed(0)}k</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Temp:</span>
              <span className="stat-value">{planet.current_temperature.toFixed(1)}°C</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Gravité:</span>
              <span className="stat-value">{planet.gravity.toFixed(2)}G</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Métal:</span>
              <span className="stat-value">{planet.metal_remaining.toLocaleString()}</span>
            </div>
          </div>
        </div>

        {/* Barres budget verticales */}
        {isOwned && (
          <div className="budget-bars-vertical">
            <div
              className="budget-bar-v"
              onClick={(e) => handleBudgetBarClick('terraform', e)}
              title={`Terra: ${terraformBudget}%`}
            >
              <div className="bar-fill terra" style={{ height: `${terraformBudget}%` }} />
              <span className="bar-label">T</span>
            </div>
            <div
              className="budget-bar-v"
              onClick={(e) => handleBudgetBarClick('mining', e)}
              title={`Mine: ${miningBudget}%`}
            >
              <div className="bar-fill mine" style={{ height: `${miningBudget}%` }} />
              <span className="bar-label">M</span>
            </div>
            <div
              className="budget-bar-v"
              onClick={(e) => handleBudgetBarClick('ships', e)}
              title={`Vsx: ${shipsBudget}%`}
            >
              <div className="bar-fill ship" style={{ height: `${shipsBudget}%` }} />
              <span className="bar-label">V</span>
            </div>
          </div>
        )}
      </div>

      {/* Bouton sauvegarder si changements */}
      {isOwned && hasChanges && (
        <button
          className="btn-save-compact"
          onClick={handleSaveBudget}
          disabled={isSaving}
        >
          {isSaving ? '...' : 'Appliquer'}
        </button>
      )}

      {/* Owner info si pas à nous */}
      {planet.owner_id && !isOwned && (
        <div className="owner-info-compact" style={{ borderColor: ownerColor }}>
          <span className="owner-dot" style={{ backgroundColor: ownerColor }} />
          <span>Colonie de {ownerName || 'inconnu'}</span>
        </div>
      )}

      {/* Modal Histoire */}
      {showHistory && (
        <div className="history-modal-overlay" onClick={() => setShowHistory(false)}>
          <div className="history-modal" onClick={(e) => e.stopPropagation()}>
            <div className="history-modal-header">
              <span>📖 Histoire de {planet.name}</span>
              <button onClick={() => setShowHistory(false)}>×</button>
            </div>
            <div className="history-modal-content">
              {planet.history_line1 && <p>{planet.history_line1}</p>}
              {planet.history_line2 && <p>{planet.history_line2}</p>}
            </div>
          </div>
        </div>
      )}

      {/* Production Queue compact */}
      {isOwned && (
        <div className="production-compact">
          <div className="production-header">
            <span>Production ({productionOutput.toFixed(0)} pts/tour)</span>
            {!showAddProduction && (
              <button
                className="btn-add-small"
                onClick={() => setShowAddProduction(true)}
                disabled={designs.length === 0}
              >
                +
              </button>
            )}
          </div>

          {productionQueue.length > 0 ? (
            <div className="queue-list-compact">
              {productionQueue.map((item) => (
                <div key={item.id} className="queue-item-compact">
                  <span className="queue-name">{item.design_name}</span>
                  <span className="queue-progress">{item.production_progress.toFixed(0)}%</span>
                  <button
                    className="queue-remove"
                    onClick={() => handleRemoveFromQueue(item.id)}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <p className="no-production-compact">Aucune production</p>
          )}

          {showAddProduction && (
            <div className="add-production-compact">
              <select
                value={selectedDesign || ''}
                onChange={(e) => setSelectedDesign(Number(e.target.value) || null)}
              >
                <option value="">Choisir...</option>
                {designs.map((design) => (
                  <option key={design.id} value={design.id}>
                    {design.name}
                  </option>
                ))}
              </select>
              <button onClick={handleAddToQueue} disabled={!selectedDesign || isSaving}>OK</button>
              <button onClick={() => { setShowAddProduction(false); setSelectedDesign(null); }}>×</button>
            </div>
          )}
        </div>
      )}

      {/* Abandon (compact) */}
      {isOwned && !planet.is_home_planet && (
        <div className="abandon-compact">
          {!showAbandonConfirm ? (
            <button
              className="btn-abandon-small"
              onClick={() => setShowAbandonConfirm(true)}
              disabled={isSaving}
            >
              Abandonner
            </button>
          ) : (
            <div className="abandon-confirm-compact">
              <label>
                <input
                  type="checkbox"
                  checked={stripMine}
                  onChange={(e) => setStripMine(e.target.checked)}
                />
                Extraire métal
              </label>
              <button className="btn-danger-small" onClick={handleAbandon} disabled={isSaving}>
                OK
              </button>
              <button onClick={() => setShowAbandonConfirm(false)}>×</button>
            </div>
          )}
        </div>
      )}

      {/* Message planète non explorée */}
      {planet.state === 'unexplored' && (
        <div className="unexplored-compact">
          <p>Planète non explorée</p>
        </div>
      )}
    </div>
  );
}

export default PlanetPanel;
