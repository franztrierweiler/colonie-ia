/**
 * ShipShowcase - Page de démonstration des vaisseaux LEGO HD
 */

import { useState } from 'react';
import ShipSprite, { ShipGallery } from '../components/game/ShipSprite';
import './ShipShowcase.css';

const SHIP_TYPES = [
  { id: 'fighter', name: 'Chasseur', desc: 'Vaisseau de combat rapide et maniable' },
  { id: 'scout', name: 'Éclaireur', desc: 'Reconnaissance et détection longue portée' },
  { id: 'colony', name: 'Vaisseau Colonial', desc: 'Transport de colons vers de nouvelles planètes' },
  { id: 'satellite', name: 'Satellite', desc: 'Station orbitale défensive' },
  { id: 'tanker', name: 'Ravitailleur', desc: 'Approvisionnement en carburant des flottes' },
  { id: 'battleship', name: 'Cuirassé', desc: 'Puissance de feu maximale' },
  { id: 'decoy', name: 'Leurre', desc: 'Vaisseau furtif et trompeur' },
  { id: 'bio', name: 'Biologique', desc: 'Technologie alien organique' },
];

function ShipShowcase() {
  const [selectedType, setSelectedType] = useState('battleship');
  const [selectedLevel, setSelectedLevel] = useState(4);
  const [battleMode, setBattleMode] = useState(false);

  return (
    <div className="ship-showcase-page">
      <div className="ship-showcase">
        <header className="showcase-header">
          <h1>Vaisseaux LEGO HD</h1>
          <p>Style LEGO Premium pour adultes - Résolution 512px</p>
        </header>

        {/* Vaisseau principal en grand */}
        <section className="showcase-main">
          <div className="main-ship-container">
            <ShipSprite
              type={selectedType}
              level={selectedLevel}
              size="full"
              animated={battleMode}
              className={battleMode ? 'propulsion' : ''}
            />
          </div>

          <div className="ship-info">
            <h2>{SHIP_TYPES.find(s => s.id === selectedType)?.name}</h2>
            <p className="ship-desc">
              {SHIP_TYPES.find(s => s.id === selectedType)?.desc}
            </p>
            <div className="level-badge">Niveau {selectedLevel}</div>
          </div>
        </section>

        {/* Contrôles */}
        <section className="showcase-controls">
          <div className="control-group">
            <label>Type de vaisseau</label>
            <div className="type-selector">
              {SHIP_TYPES.map(ship => (
                <button
                  key={ship.id}
                  className={`type-btn ${selectedType === ship.id ? 'active' : ''}`}
                  onClick={() => setSelectedType(ship.id)}
                >
                  <ShipSprite type={ship.id} level={selectedLevel} size="sm" />
                  <span>{ship.name}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="control-group">
            <label>Niveau technologique</label>
            <div className="level-selector">
              {[1, 2, 3, 4].map(level => (
                <button
                  key={level}
                  className={`level-btn ${selectedLevel === level ? 'active' : ''}`}
                  onClick={() => setSelectedLevel(level)}
                >
                  Nv.{level}
                </button>
              ))}
            </div>
          </div>

          <div className="control-group">
            <label>Mode bataille</label>
            <button
              className={`toggle-btn ${battleMode ? 'active' : ''}`}
              onClick={() => setBattleMode(!battleMode)}
            >
              {battleMode ? 'Activé' : 'Désactivé'}
            </button>
          </div>
        </section>

        {/* Comparaison des tailles */}
        <section className="showcase-sizes">
          <h3>Comparaison des tailles d'affichage</h3>
          <div className="sizes-grid">
            <div className="size-item">
              <ShipSprite type={selectedType} level={selectedLevel} size="xs" />
              <span>xs (24px) - Mini icônes</span>
            </div>
            <div className="size-item">
              <ShipSprite type={selectedType} level={selectedLevel} size="sm" />
              <span>sm (32px) - Menus</span>
            </div>
            <div className="size-item">
              <ShipSprite type={selectedType} level={selectedLevel} size="md" />
              <span>md (64px) - Listes</span>
            </div>
            <div className="size-item">
              <ShipSprite type={selectedType} level={selectedLevel} size="lg" />
              <span>lg (128px) - Détails</span>
            </div>
            <div className="size-item">
              <ShipSprite type={selectedType} level={selectedLevel} size="xl" />
              <span>xl (192px) - Batailles</span>
            </div>
          </div>
        </section>

        {/* Galerie complète */}
        <section className="showcase-gallery">
          <ShipGallery />
        </section>

        {/* Simulation de flotte */}
        <section className="showcase-fleet">
          <h3>Simulation de flotte en bataille</h3>
          <div className="fleet-simulation">
            <div className="fleet-side fleet-left">
              <h4>Flotte Alpha</h4>
              <div className="fleet-ships">
                <ShipSprite type="battleship" level={4} size="xl" animated />
                <ShipSprite type="fighter" level={3} size="lg" animated />
                <ShipSprite type="fighter" level={3} size="lg" animated />
                <ShipSprite type="scout" level={2} size="md" animated />
              </div>
            </div>
            <div className="fleet-vs">VS</div>
            <div className="fleet-side fleet-right">
              <h4>Flotte Omega</h4>
              <div className="fleet-ships mirrored">
                <ShipSprite type="bio" level={4} size="xl" animated />
                <ShipSprite type="bio" level={3} size="lg" animated />
                <ShipSprite type="decoy" level={2} size="md" animated />
                <ShipSprite type="decoy" level={2} size="md" animated />
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

export default ShipShowcase;
