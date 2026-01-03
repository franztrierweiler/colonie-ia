import { useState, useEffect, useCallback } from 'react';
import api from '../../services/api';
import type {
  PlayerTechnology,
  TechBudget,
  RadicalBreakthrough,
} from '../../services/api';
import './TechPanel.css';

interface TechPanelProps {
  gameId: number;
  onBreakthroughClick?: (breakthrough: RadicalBreakthrough) => void;
  onComparisonClick?: () => void;
}

interface TechDomain {
  key: keyof TechBudget;
  levelKey: 'range' | 'speed' | 'weapons' | 'shields' | 'mini' | 'radical';
  label: string;
  shortLabel: string;
  color: string;
}

const TECH_DOMAINS: TechDomain[] = [
  { key: 'range_budget', levelKey: 'range', label: 'Portee', shortLabel: 'Port.', color: '#4a9eff' },
  { key: 'speed_budget', levelKey: 'speed', label: 'Vitesse', shortLabel: 'Vit.', color: '#50c878' },
  { key: 'weapons_budget', levelKey: 'weapons', label: 'Armes', shortLabel: 'Armes', color: '#ff6b6b' },
  { key: 'shields_budget', levelKey: 'shields', label: 'Boucliers', shortLabel: 'Boucl.', color: '#9370db' },
  { key: 'mini_budget', levelKey: 'mini', label: 'Miniaturisation', shortLabel: 'Mini.', color: '#ffa500' },
  { key: 'radical_budget', levelKey: 'radical', label: 'Radical', shortLabel: 'Rad.', color: '#ff1493' },
];

function TechPanel({ gameId, onBreakthroughClick, onComparisonClick }: TechPanelProps) {
  const [technology, setTechnology] = useState<PlayerTechnology | null>(null);
  const [pendingBreakthroughs, setPendingBreakthroughs] = useState<RadicalBreakthrough[]>([]);
  const [isEditing, setIsEditing] = useState(false);
  const [editBudget, setEditBudget] = useState<TechBudget | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadTechnology = useCallback(async () => {
    try {
      const data = await api.getTechnology(gameId);
      setTechnology(data);
      setError(null);
    } catch (err) {
      console.error('Erreur chargement technologie:', err);
      setError('Erreur de chargement');
    }
  }, [gameId]);

  const loadBreakthroughs = useCallback(async () => {
    try {
      const data = await api.getPendingBreakthroughs(gameId);
      setPendingBreakthroughs(data.pending);
    } catch (err) {
      console.error('Erreur chargement percees:', err);
    }
  }, [gameId]);

  useEffect(() => {
    loadTechnology();
    loadBreakthroughs();
  }, [loadTechnology, loadBreakthroughs]);

  const startEditing = () => {
    if (!technology) return;
    setEditBudget({
      range_budget: technology.budget.range,
      speed_budget: technology.budget.speed,
      weapons_budget: technology.budget.weapons,
      shields_budget: technology.budget.shields,
      mini_budget: technology.budget.mini,
      radical_budget: technology.budget.radical,
    });
    setIsEditing(true);
  };

  const cancelEditing = () => {
    setIsEditing(false);
    setEditBudget(null);
  };

  const saveBudget = async () => {
    if (!editBudget) return;

    // Verify total is 100
    const total = Object.values(editBudget).reduce((sum, val) => sum + val, 0);
    if (total !== 100) {
      setError(`Le total doit etre 100% (actuellement ${total}%)`);
      return;
    }

    setIsSaving(true);
    try {
      await api.updateResearchBudget(gameId, editBudget);
      await loadTechnology();
      setIsEditing(false);
      setEditBudget(null);
      setError(null);
    } catch (err) {
      console.error('Erreur sauvegarde budget:', err);
      setError('Erreur de sauvegarde');
    } finally {
      setIsSaving(false);
    }
  };

  const adjustBudget = (key: keyof TechBudget, delta: number) => {
    if (!editBudget) return;

    const current = editBudget[key];
    const newValue = Math.max(0, Math.min(100, current + delta));
    const actualDelta = newValue - current;

    if (actualDelta === 0) return;

    // Redistribute the delta across other domains
    const otherKeys = TECH_DOMAINS.filter((d) => d.key !== key).map((d) => d.key);
    const redistributePerDomain = -actualDelta / otherKeys.length;

    const newBudget = { ...editBudget, [key]: newValue };

    // Try to redistribute evenly
    let remaining = -actualDelta;
    for (const otherKey of otherKeys) {
      const otherCurrent = newBudget[otherKey];
      const otherNew = Math.max(0, Math.min(100, Math.round(otherCurrent + redistributePerDomain)));
      const otherActual = otherNew - otherCurrent;
      remaining += otherActual;
      newBudget[otherKey] = otherNew;
    }

    // Fix any rounding errors on the last adjustable domain
    if (remaining !== 0) {
      for (const otherKey of otherKeys) {
        const adjusted = newBudget[otherKey] - remaining;
        if (adjusted >= 0 && adjusted <= 100) {
          newBudget[otherKey] = adjusted;
          break;
        }
      }
    }

    setEditBudget(newBudget);
  };

  if (!technology) {
    return (
      <section className="bottom-panel tech-panel">
        <h4>Technologie</h4>
        <div className="tech-loading">Chargement...</div>
      </section>
    );
  }

  const currentBudget = isEditing && editBudget ? editBudget : {
    range_budget: technology.budget.range,
    speed_budget: technology.budget.speed,
    weapons_budget: technology.budget.weapons,
    shields_budget: technology.budget.shields,
    mini_budget: technology.budget.mini,
    radical_budget: technology.budget.radical,
  };

  const totalBudget = Object.values(currentBudget).reduce((sum, val) => sum + val, 0);
  const hasPendingBreakthrough = pendingBreakthroughs.length > 0;

  return (
    <section className="bottom-panel tech-panel">
      <div className="tech-header">
        <h4>Technologie</h4>
        <div className="tech-actions">
          {onComparisonClick && (
            <button
              className="btn-tech-compare"
              onClick={onComparisonClick}
              title="Comparer avec adversaires"
            >
              Comparer
            </button>
          )}
          {isEditing ? (
            <>
              <button
                className="btn-tech-cancel"
                onClick={cancelEditing}
                disabled={isSaving}
              >
                Annuler
              </button>
              <button
                className="btn-tech-save"
                onClick={saveBudget}
                disabled={isSaving || totalBudget !== 100}
              >
                {isSaving ? '...' : 'Sauver'}
              </button>
            </>
          ) : (
            <button className="btn-tech-edit" onClick={startEditing}>
              Modifier
            </button>
          )}
        </div>
      </div>

      {error && <div className="tech-error">{error}</div>}

      {isEditing && totalBudget !== 100 && (
        <div className="tech-warning">
          Total: {totalBudget}% (doit etre 100%)
        </div>
      )}

      <div className="tech-bars-vertical">
        {TECH_DOMAINS.map((domain) => {
          const level = technology.levels[domain.levelKey];
          const progress = technology.progress_percentages?.[domain.levelKey] || 0;
          const budget = currentBudget[domain.key];
          const effectiveLevel = technology.effective_levels?.[domain.levelKey as keyof typeof technology.effective_levels];
          const hasBonus = effectiveLevel !== undefined && effectiveLevel > level;
          const isRadical = domain.levelKey === 'radical';

          return (
            <div
              key={domain.key}
              className={`tech-bar-v ${isEditing ? 'editing' : ''} ${isRadical && hasPendingBreakthrough ? 'has-breakthrough' : ''}`}
              title={`${domain.label}: Niveau ${level}, Budget ${budget}%, Progression ${progress.toFixed(0)}%`}
              style={{ '--tech-color': domain.color } as React.CSSProperties}
            >
              {/* Level display */}
              <span className="tech-bar-value">
                {level}
                {hasBonus && <span className="tech-bonus">+{effectiveLevel! - level}</span>}
              </span>

              {/* Progress indicator */}
              <div
                className="tech-progress-v"
                style={{ height: `${progress}%` }}
              />

              {/* Budget fill */}
              <div
                className="tech-fill-v"
                style={{
                  height: `${budget}%`,
                  background: `linear-gradient(to top, ${domain.color}cc, ${domain.color}66)`,
                }}
              />

              {/* Label */}
              <span className="tech-bar-label">{domain.shortLabel}</span>

              {/* Budget controls when editing */}
              {isEditing && (
                <div className="tech-budget-controls">
                  <button
                    className="budget-btn up"
                    onClick={() => adjustBudget(domain.key, 5)}
                  >
                    +
                  </button>
                  <span className="budget-pct">{budget}%</span>
                  <button
                    className="budget-btn down"
                    onClick={() => adjustBudget(domain.key, -5)}
                  >
                    -
                  </button>
                </div>
              )}

              {/* Breakthrough indicator */}
              {isRadical && hasPendingBreakthrough && (
                <button
                  className="breakthrough-indicator"
                  onClick={() => onBreakthroughClick?.(pendingBreakthroughs[0])}
                  title="Percee radicale en attente!"
                >
                  !
                </button>
              )}
            </div>
          );
        })}
      </div>

      {/* Unlocks display */}
      {(technology.unlocks.decoy || technology.unlocks.biological) && (
        <div className="tech-unlocks">
          {technology.unlocks.decoy && <span className="unlock-badge">Leurre</span>}
          {technology.unlocks.biological && <span className="unlock-badge">Bio</span>}
        </div>
      )}
    </section>
  );
}

export default TechPanel;
