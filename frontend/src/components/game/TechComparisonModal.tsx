import { useState, useEffect } from 'react';
import api from '../../services/api';
import type { TechComparison } from '../../services/api';
import './TechComparisonModal.css';

interface TechComparisonModalProps {
  gameId: number;
  isOpen: boolean;
  onClose: () => void;
}

const TECH_DOMAINS = [
  { key: 'range' as const, label: 'Portee', icon: '>' },
  { key: 'speed' as const, label: 'Vitesse', icon: 'v' },
  { key: 'weapons' as const, label: 'Armes', icon: 'x' },
  { key: 'shields' as const, label: 'Boucliers', icon: 'O' },
  { key: 'mini' as const, label: 'Mini', icon: 'm' },
];

function TechComparisonModal({ gameId, isOpen, onClose }: TechComparisonModalProps) {
  const [comparison, setComparison] = useState<TechComparison | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;

    const loadComparison = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await api.getTechComparison(gameId);
        setComparison(data);
      } catch (err) {
        console.error('Erreur chargement comparaison:', err);
        setError('Erreur de chargement');
      } finally {
        setIsLoading(false);
      }
    };

    loadComparison();
  }, [gameId, isOpen]);

  if (!isOpen) return null;

  const getRelativeIcon = (status: 'ahead' | 'behind' | 'equal') => {
    switch (status) {
      case 'ahead':
        return { icon: '+', className: 'ahead' };
      case 'behind':
        return { icon: '-', className: 'behind' };
      case 'equal':
        return { icon: '=', className: 'equal' };
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="tech-comparison-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Comparaison Technologique</h3>
          <button className="modal-close" onClick={onClose}>
            x
          </button>
        </div>

        <div className="modal-content">
          {isLoading && <div className="loading">Chargement...</div>}
          {error && <div className="error">{error}</div>}

          {comparison && (
            <>
              {/* Your levels */}
              <div className="your-levels">
                <h4>Vos niveaux</h4>
                <div className="level-row">
                  {TECH_DOMAINS.map((domain) => (
                    <div key={domain.key} className="level-item">
                      <span className="level-label">{domain.label}</span>
                      <span className="level-value">
                        {comparison.your_levels[domain.key]}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Opponent comparison */}
              <div className="opponents-section">
                <h4>Adversaires</h4>
                {comparison.opponents.length === 0 ? (
                  <p className="no-opponents">Aucun adversaire</p>
                ) : (
                  <table className="comparison-table">
                    <thead>
                      <tr>
                        <th>Joueur</th>
                        {TECH_DOMAINS.map((domain) => (
                          <th key={domain.key} title={domain.label}>
                            {domain.icon}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {comparison.opponents.map((opponent) => (
                        <tr key={opponent.player_id}>
                          <td>
                            <span
                              className="player-dot"
                              style={{ backgroundColor: opponent.color }}
                            />
                            <span className="player-name">
                              {opponent.player_name}
                            </span>
                          </td>
                          {TECH_DOMAINS.map((domain) => {
                            const status = opponent.relative[domain.key];
                            const { icon, className } = getRelativeIcon(status);
                            return (
                              <td
                                key={domain.key}
                                className={`relative-cell ${className}`}
                                title={
                                  status === 'ahead'
                                    ? 'Vous etes en avance'
                                    : status === 'behind'
                                      ? 'Vous etes en retard'
                                      : 'A egalite'
                                }
                              >
                                {icon}
                              </td>
                            );
                          })}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>

              <div className="legend">
                <span className="legend-item ahead">+ En avance</span>
                <span className="legend-item equal">= Egal</span>
                <span className="legend-item behind">- En retard</span>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default TechComparisonModal;
