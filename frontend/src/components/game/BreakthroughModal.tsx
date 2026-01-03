import { useState } from 'react';
import api from '../../services/api';
import type { RadicalBreakthrough, BreakthroughEffect } from '../../services/api';
import './BreakthroughModal.css';

interface BreakthroughModalProps {
  breakthrough: RadicalBreakthrough;
  isOpen: boolean;
  onClose: () => void;
  onResolved?: (effect: BreakthroughEffect) => void;
}

// Descriptions des types de percees
const BREAKTHROUGH_INFO: Record<string, { label: string; description: string; icon: string }> = {
  tech_bonus_range: {
    label: 'Bonus Portee',
    description: '+2 niveaux de Portee pendant 5 tours',
    icon: '>',
  },
  tech_bonus_speed: {
    label: 'Bonus Vitesse',
    description: '+2 niveaux de Vitesse pendant 5 tours',
    icon: 'v',
  },
  tech_bonus_weapons: {
    label: 'Bonus Armes',
    description: '+2 niveaux d\'Armes pendant 5 tours',
    icon: 'x',
  },
  tech_bonus_shields: {
    label: 'Bonus Boucliers',
    description: '+2 niveaux de Boucliers pendant 5 tours',
    icon: 'O',
  },
  terraform_boost: {
    label: 'Terraformation Acceleree',
    description: 'Vitesse de terraformation x2 pendant 3 tours',
    icon: 'T',
  },
  spy_info: {
    label: 'Espionnage',
    description: 'Revele les infos des planetes ennemies',
    icon: '?',
  },
  steal_tech: {
    label: 'Vol de Technologie',
    description: 'Vole une technologie a un adversaire aleatoire',
    icon: '*',
  },
  unlock_decoy: {
    label: 'Vaisseaux Leurre',
    description: 'Debloque la construction de vaisseaux Leurre',
    icon: 'L',
  },
  unlock_biological: {
    label: 'Vaisseaux Biologiques',
    description: 'Debloque la construction de vaisseaux Biologiques',
    icon: 'B',
  },
};

function BreakthroughModal({
  breakthrough,
  isOpen,
  onClose,
  onResolved,
}: BreakthroughModalProps) {
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [isEliminating, setIsEliminating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{
    eliminated: string;
    unlocked: string;
    effect: BreakthroughEffect;
  } | null>(null);

  if (!isOpen) return null;

  const handleEliminate = async () => {
    if (!selectedOption) return;

    setIsEliminating(true);
    setError(null);

    try {
      const response = await api.eliminateBreakthroughOption(
        breakthrough.id,
        selectedOption
      );

      setResult({
        eliminated: selectedOption,
        unlocked: response.breakthrough.unlocked_option!,
        effect: response.effect,
      });

      onResolved?.(response.effect);
    } catch (err) {
      console.error('Erreur elimination percee:', err);
      setError('Erreur lors de la resolution');
    } finally {
      setIsEliminating(false);
    }
  };

  const getOptionInfo = (option: string) => {
    return BREAKTHROUGH_INFO[option] || {
      label: option,
      description: 'Effet inconnu',
      icon: '?',
    };
  };

  // Mode resultat : afficher ce qui a ete debloque
  if (result) {
    const unlockedInfo = getOptionInfo(result.unlocked);

    return (
      <div className="modal-overlay" onClick={onClose}>
        <div className="breakthrough-modal result-mode" onClick={(e) => e.stopPropagation()}>
          <div className="modal-header">
            <h3>Percee Radicale !</h3>
          </div>

          <div className="modal-content">
            <div className="result-section">
              <div className="result-icon success">{unlockedInfo.icon}</div>
              <h4 className="result-title">{unlockedInfo.label}</h4>
              <p className="result-description">{unlockedInfo.description}</p>

              {result.effect.bonus_value && (
                <div className="result-detail">
                  Bonus : +{result.effect.bonus_value} niveaux
                </div>
              )}
              {result.effect.expires_turn && (
                <div className="result-detail">
                  Expire au tour {result.effect.expires_turn}
                </div>
              )}
              {result.effect.unlock && (
                <div className="result-detail">
                  Nouveau type de vaisseau disponible !
                </div>
              )}
            </div>

            <button className="btn-close-result" onClick={onClose}>
              Fermer
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Mode selection : choisir l'option a eliminer
  return (
    <div className="modal-overlay">
      <div className="breakthrough-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Percee Radicale</h3>
          <span className="turn-info">Tour {breakthrough.created_turn}</span>
        </div>

        <div className="modal-content">
          <p className="instructions">
            Choisissez l'option a <strong>eliminer</strong>. Une des trois
            restantes sera deverrouillee aleatoirement.
          </p>

          {error && <div className="error-message">{error}</div>}

          <div className="options-grid">
            {breakthrough.options.map((option) => {
              const info = getOptionInfo(option);
              const isSelected = selectedOption === option;

              return (
                <button
                  key={option}
                  className={`option-card ${isSelected ? 'selected' : ''}`}
                  onClick={() => setSelectedOption(option)}
                  disabled={isEliminating}
                >
                  <div className="option-icon">{info.icon}</div>
                  <div className="option-label">{info.label}</div>
                  <div className="option-description">{info.description}</div>
                  {isSelected && (
                    <div className="eliminate-badge">A eliminer</div>
                  )}
                </button>
              );
            })}
          </div>

          <div className="modal-actions">
            <button
              className="btn-eliminate"
              onClick={handleEliminate}
              disabled={!selectedOption || isEliminating}
            >
              {isEliminating ? 'Resolution...' : 'Eliminer cette option'}
            </button>
          </div>

          <p className="hint">
            Conseil : eliminez l'option la moins utile pour maximiser vos
            chances d'obtenir ce que vous voulez.
          </p>
        </div>
      </div>
    </div>
  );
}

export default BreakthroughModal;
