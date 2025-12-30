import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { PixelPlanet, PixelChevron } from '../components/PixelIcons';
import './CreateGame.css';

type GalaxyShape = 'circle' | 'spiral' | 'cluster' | 'random';
type GalaxySize = 'small' | 'medium' | 'large' | 'huge';
type GalaxyDensity = 'low' | 'medium' | 'high';

interface GameConfig {
  name: string;
  galaxy_shape: GalaxyShape;
  galaxy_size: GalaxySize;
  galaxy_density: GalaxyDensity;
  max_players: number;
  turn_duration_years: number;
  alliances_enabled: boolean;
  combat_luck_enabled: boolean;
}

const SHAPE_LABELS: Record<GalaxyShape, string> = {
  circle: 'Cercle',
  spiral: 'Spirale',
  cluster: 'Amas',
  random: 'Aléatoire',
};

const SIZE_LABELS: Record<GalaxySize, { label: string; stars: number; duration: string }> = {
  small: { label: 'Petite', stars: 20, duration: '15-30 min' },
  medium: { label: 'Moyenne', stars: 50, duration: '30-45 min' },
  large: { label: 'Grande', stars: 100, duration: '45-60 min' },
  huge: { label: 'Immense', stars: 200, duration: '60+ min' },
};

const DENSITY_LABELS: Record<GalaxyDensity, string> = {
  low: 'Faible',
  medium: 'Normale',
  high: 'Élevée',
};

function CreateGame() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const [config, setConfig] = useState<GameConfig>({
    name: '',
    galaxy_shape: 'spiral',
    galaxy_size: 'medium',
    galaxy_density: 'medium',
    max_players: 4,
    turn_duration_years: 10,
    alliances_enabled: true,
    combat_luck_enabled: true,
  });
  const [nameError, setNameError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setNameError(null);

    // Validation
    if (!config.name.trim()) {
      setNameError('Le nom de la partie est requis');
      return;
    }
    if (config.name.trim().length < 3) {
      setNameError('Le nom doit contenir au moins 3 caractères');
      return;
    }

    setIsLoading(true);

    try {
      const game = await api.createGame(config);
      navigate(`/games/${game.id}/lobby`);
    } catch (err) {
      console.error('Erreur création partie:', err);
      const message = err instanceof Error ? err.message : 'Erreur lors de la création de la partie';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const updateConfig = <K extends keyof GameConfig>(key: K, value: GameConfig[K]) => {
    setConfig((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <div className="create-game-page">
      <div className="create-game-card">
        <div className="create-game-header">
          <button className="back-btn" onClick={() => navigate('/games')}>
            <PixelChevron size={16} direction="left" />
            Retour
          </button>
          <h1>Nouvelle Partie</h1>
        </div>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="create-game-form">
          <div className="form-group">
            <label htmlFor="game-name">Nom de la partie</label>
            <input
              id="game-name"
              type="text"
              value={config.name}
              onChange={(e) => {
                updateConfig('name', e.target.value);
                if (nameError) setNameError(null);
              }}
              placeholder="Campagne d'Austerlitz"
              maxLength={100}
              className={nameError ? 'input-error' : ''}
            />
            {nameError && <span className="field-error">{nameError}</span>}
          </div>

          <div className="form-section">
            <h3>Galaxie</h3>

            <div className="form-group">
              <label>Forme</label>
              <div className="option-grid">
                {(Object.keys(SHAPE_LABELS) as GalaxyShape[]).map((shape) => (
                  <button
                    key={shape}
                    type="button"
                    className={`option-btn ${config.galaxy_shape === shape ? 'active' : ''}`}
                    onClick={() => updateConfig('galaxy_shape', shape)}
                  >
                    {SHAPE_LABELS[shape]}
                  </button>
                ))}
              </div>
            </div>

            <div className="form-group">
              <label>Taille</label>
              <div className="size-options">
                {(Object.keys(SIZE_LABELS) as GalaxySize[]).map((size) => (
                  <button
                    key={size}
                    type="button"
                    className={`size-option ${config.galaxy_size === size ? 'active' : ''}`}
                    onClick={() => updateConfig('galaxy_size', size)}
                  >
                    <span className="size-label">{SIZE_LABELS[size].label}</span>
                    <span className="size-stars">{SIZE_LABELS[size].stars} étoiles</span>
                    <span className="size-duration">{SIZE_LABELS[size].duration}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="form-group">
              <label>Densité stellaire</label>
              <div className="option-grid three-cols">
                {(Object.keys(DENSITY_LABELS) as GalaxyDensity[]).map((density) => (
                  <button
                    key={density}
                    type="button"
                    className={`option-btn ${config.galaxy_density === density ? 'active' : ''}`}
                    onClick={() => updateConfig('galaxy_density', density)}
                  >
                    {DENSITY_LABELS[density]}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="form-section">
            <h3>Joueurs</h3>

            <div className="form-group">
              <label htmlFor="max-players">Nombre maximum de joueurs</label>
              <div className="slider-group">
                <input
                  id="max-players"
                  type="range"
                  min="2"
                  max="8"
                  value={config.max_players}
                  onChange={(e) => updateConfig('max_players', parseInt(e.target.value))}
                />
                <span className="slider-value">{config.max_players}</span>
              </div>
            </div>
          </div>

          <button
            type="button"
            className="advanced-toggle"
            onClick={() => setShowAdvanced(!showAdvanced)}
          >
            Options avancées
            <PixelChevron size={12} direction={showAdvanced ? 'up' : 'down'} />
          </button>

          {showAdvanced && (
            <div className="form-section advanced">
              <div className="form-group">
                <label htmlFor="turn-duration">Durée des tours (années)</label>
                <div className="slider-group">
                  <input
                    id="turn-duration"
                    type="range"
                    min="10"
                    max="50"
                    step="5"
                    value={config.turn_duration_years}
                    onChange={(e) => updateConfig('turn_duration_years', parseInt(e.target.value))}
                  />
                  <span className="slider-value">{config.turn_duration_years} ans</span>
                </div>
              </div>

              <div className="form-group checkbox-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={config.alliances_enabled}
                    onChange={(e) => updateConfig('alliances_enabled', e.target.checked)}
                  />
                  <span className="checkbox-text">Alliances autorisées</span>
                </label>
              </div>

              <div className="form-group checkbox-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={config.combat_luck_enabled}
                    onChange={(e) => updateConfig('combat_luck_enabled', e.target.checked)}
                  />
                  <span className="checkbox-text">Chance au combat</span>
                </label>
              </div>
            </div>
          )}

          <div className="form-actions">
            <button
              type="button"
              className="btn-secondary"
              onClick={() => navigate('/games')}
            >
              Annuler
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={isLoading}
            >
              {isLoading ? (
                'Création...'
              ) : (
                <>
                  <PixelPlanet size={18} />
                  Créer la partie
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateGame;
