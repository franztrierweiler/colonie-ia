import { useState, useCallback } from 'react';
import type { Planet, Player } from '../../hooks/useGameState';
import BudgetSlider from './BudgetSlider';
import api from '../../services/api';
import './PlanetPanel.css';

interface PlanetPanelProps {
  planet: Planet;
  starName: string;
  isOwned: boolean;
  ownerColor: string;
  ownerName?: string;
  onClose: () => void;
  onBudgetChange: () => void;
  onAbandon: () => void;
}

function PlanetPanel({
  planet,
  starName,
  isOwned,
  ownerColor,
  ownerName,
  onClose,
  onBudgetChange,
  onAbandon,
}: PlanetPanelProps) {
  const [terraformBudget, setTerraformBudget] = useState(planet.terraform_budget);
  const [miningBudget, setMiningBudget] = useState(planet.mining_budget);
  const [isSaving, setIsSaving] = useState(false);
  const [showAbandonConfirm, setShowAbandonConfirm] = useState(false);
  const [stripMine, setStripMine] = useState(true);

  const hasChanges =
    terraformBudget !== planet.terraform_budget || miningBudget !== planet.mining_budget;

  const handleTerraformChange = useCallback((value: number) => {
    setTerraformBudget(value);
    setMiningBudget(100 - value);
  }, []);

  const handleMiningChange = useCallback((value: number) => {
    setMiningBudget(value);
    setTerraformBudget(100 - value);
  }, []);

  const handleSaveBudget = async () => {
    setIsSaving(true);
    try {
      await api.updatePlanetBudget(planet.id, terraformBudget, miningBudget);
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
      console.error('Erreur lors de l\'abandon:', err);
    } finally {
      setIsSaving(false);
    }
  };

  // Calcul des indicateurs
  const tempDiff = Math.abs(planet.current_temperature - 22);
  const tempStatus = tempDiff <= 5 ? 'optimal' : tempDiff <= 20 ? 'acceptable' : 'hostile';
  const gravityDiff = Math.abs(planet.gravity - 1.0);
  const gravityStatus = gravityDiff <= 0.2 ? 'optimal' : gravityDiff <= 0.5 ? 'acceptable' : 'hostile';

  return (
    <div className="planet-panel">
      <div className="panel-header">
        <div className="planet-title">
          <h2>{planet.name}</h2>
          {planet.is_home_planet && <span className="home-badge">Capitale</span>}
        </div>
        <button className="close-btn" onClick={onClose}>
          ×
        </button>
      </div>

      <p className="planet-location">
        Orbite {planet.orbit_index + 1} de {starName}
      </p>

      {/* Owner info */}
      {planet.owner_id && (
        <div className="owner-info" style={{ borderColor: ownerColor }}>
          <span className="owner-dot" style={{ backgroundColor: ownerColor }} />
          <span>{isOwned ? 'Votre colonie' : `Colonie de ${ownerName || 'inconnu'}`}</span>
        </div>
      )}

      {/* Characteristics */}
      <section className="planet-section">
        <h3>Caractéristiques</h3>
        <div className="characteristics-grid">
          <div className={`characteristic ${tempStatus}`}>
            <span className="char-label">Température</span>
            <span className="char-value">{planet.current_temperature.toFixed(1)}°C</span>
            {planet.current_temperature !== planet.temperature && (
              <span className="char-original">(base: {planet.temperature.toFixed(1)}°C)</span>
            )}
          </div>
          <div className={`characteristic ${gravityStatus}`}>
            <span className="char-label">Gravité</span>
            <span className="char-value">{planet.gravity.toFixed(2)}g</span>
          </div>
          <div className="characteristic">
            <span className="char-label">Habitabilité</span>
            <span className="char-value">{(planet.habitability * 100).toFixed(0)}%</span>
          </div>
          <div className="characteristic">
            <span className="char-label">Métal restant</span>
            <span className="char-value">{planet.metal_remaining.toLocaleString()}</span>
            <span className="char-original">/ {planet.metal_reserves.toLocaleString()}</span>
          </div>
        </div>
      </section>

      {/* Population (only if colonized) */}
      {planet.state !== 'unexplored' && planet.state !== 'explored' && (
        <section className="planet-section">
          <h3>Population</h3>
          <div className="population-bar-container">
            <div className="population-info">
              <span>{(planet.population / 1000).toFixed(0)}k</span>
              <span className="population-max">/ {(planet.max_population / 1000).toFixed(0)}k</span>
            </div>
            <div className="population-bar">
              <div
                className="population-fill"
                style={{
                  width: `${planet.max_population > 0 ? (planet.population / planet.max_population) * 100 : 0}%`,
                }}
              />
            </div>
          </div>
        </section>
      )}

      {/* Budget sliders (only if owned) */}
      {isOwned && (
        <section className="planet-section">
          <h3>Allocation du budget</h3>
          <BudgetSlider
            label="Terraformation"
            value={terraformBudget}
            onChange={handleTerraformChange}
            color="#4a9eff"
            disabled={isSaving}
          />
          <BudgetSlider
            label="Extraction minière"
            value={miningBudget}
            onChange={handleMiningChange}
            color="#ffa500"
            disabled={isSaving}
          />

          {hasChanges && (
            <button
              className="btn-primary btn-save-budget"
              onClick={handleSaveBudget}
              disabled={isSaving}
            >
              {isSaving ? 'Sauvegarde...' : 'Appliquer'}
            </button>
          )}
        </section>
      )}

      {/* Abandon button (only if owned and not home planet) */}
      {isOwned && !planet.is_home_planet && (
        <section className="planet-section danger-section">
          {!showAbandonConfirm ? (
            <button
              className="btn-danger"
              onClick={() => setShowAbandonConfirm(true)}
              disabled={isSaving}
            >
              Abandonner la planète
            </button>
          ) : (
            <div className="abandon-confirm">
              <p>Êtes-vous sûr de vouloir abandonner cette planète ?</p>
              <label className="strip-mine-option">
                <input
                  type="checkbox"
                  checked={stripMine}
                  onChange={(e) => setStripMine(e.target.checked)}
                />
                Extraire le métal restant avant abandon
              </label>
              <div className="abandon-buttons">
                <button
                  className="btn-danger"
                  onClick={handleAbandon}
                  disabled={isSaving}
                >
                  {isSaving ? 'En cours...' : 'Confirmer l\'abandon'}
                </button>
                <button
                  className="btn-secondary"
                  onClick={() => setShowAbandonConfirm(false)}
                  disabled={isSaving}
                >
                  Annuler
                </button>
              </div>
            </div>
          )}
        </section>
      )}

      {/* Unexplored planet message */}
      {planet.state === 'unexplored' && (
        <div className="unexplored-message">
          <p>Cette planète n'a pas encore été explorée.</p>
          <p>Envoyez un vaisseau pour découvrir ses caractéristiques.</p>
        </div>
      )}
    </div>
  );
}

export default PlanetPanel;
