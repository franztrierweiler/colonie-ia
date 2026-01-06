/**
 * ShipSelectionModal - Modale de sélection des vaisseaux à envoyer
 * Affiche les vaisseaux par type avec compteurs +/-
 */
import { useState, useMemo } from 'react';
import { SHIP_TYPES } from '../../hooks/useGameState';
import './ShipSelectionModal.css';

interface ShipSelectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  availableShips: Record<string, number>;
  planetName: string;
  onSelectionComplete: (selection: Record<string, number>) => void;
}

function ShipSelectionModal({
  isOpen,
  onClose,
  availableShips,
  planetName,
  onSelectionComplete,
}: ShipSelectionModalProps) {
  const [selection, setSelection] = useState<Record<string, number>>({});

  // Calculer le total sélectionné
  const totalSelected = useMemo(() => {
    return Object.values(selection).reduce((sum, count) => sum + count, 0);
  }, [selection]);

  // Types de vaisseaux disponibles (non vides)
  const availableTypes = useMemo(() => {
    return Object.entries(availableShips)
      .filter(([, count]) => count > 0)
      .sort((a, b) => a[0].localeCompare(b[0]));
  }, [availableShips]);

  if (!isOpen) return null;

  const handleIncrement = (type: string) => {
    const current = selection[type] || 0;
    const max = availableShips[type] || 0;
    if (current < max) {
      setSelection({ ...selection, [type]: current + 1 });
    }
  };

  const handleDecrement = (type: string) => {
    const current = selection[type] || 0;
    if (current > 0) {
      setSelection({ ...selection, [type]: current - 1 });
    }
  };

  const handleSelectAll = () => {
    setSelection({ ...availableShips });
  };

  const handleClearAll = () => {
    setSelection({});
  };

  const handleConfirm = () => {
    if (totalSelected > 0) {
      // Filtrer les entrées avec count > 0
      const filtered = Object.fromEntries(
        Object.entries(selection).filter(([, count]) => count > 0)
      );
      onSelectionComplete(filtered);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="ship-selection-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Envoyer des vaisseaux</h3>
          <span className="planet-origin">depuis {planetName}</span>
          <button className="btn-close" onClick={onClose}>×</button>
        </div>

        <div className="modal-content">
          {availableTypes.length === 0 ? (
            <p className="no-ships">Aucun vaisseau disponible sur cette planète</p>
          ) : (
            <>
              <div className="ship-types-list">
                {availableTypes.map(([type, available]) => {
                  const shipInfo = SHIP_TYPES[type as keyof typeof SHIP_TYPES];
                  const selected = selection[type] || 0;

                  return (
                    <div key={type} className="ship-type-row">
                      <span className="ship-icon">{shipInfo?.icon || '?'}</span>
                      <span className="ship-name">{shipInfo?.name || type}</span>
                      <div className="ship-counter">
                        <button
                          className="btn-counter"
                          onClick={() => handleDecrement(type)}
                          disabled={selected === 0}
                        >
                          -
                        </button>
                        <span className="counter-value">
                          {selected} / {available}
                        </span>
                        <button
                          className="btn-counter"
                          onClick={() => handleIncrement(type)}
                          disabled={selected >= available}
                        >
                          +
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>

              <div className="selection-summary">
                <span className="total-label">Total sélectionné :</span>
                <span className="total-count">{totalSelected}</span>
              </div>
            </>
          )}
        </div>

        <div className="modal-actions">
          <div className="quick-actions">
            <button className="btn-secondary" onClick={handleSelectAll}>
              Tout
            </button>
            <button className="btn-secondary" onClick={handleClearAll}>
              Aucun
            </button>
          </div>
          <button
            className="btn-primary"
            onClick={handleConfirm}
            disabled={totalSelected === 0}
          >
            Sélection terminée
          </button>
        </div>
      </div>
    </div>
  );
}

export default ShipSelectionModal;
