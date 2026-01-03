/**
 * ShipSprite - Affiche un sprite de vaisseau LEGO HD
 *
 * Les sprites sont en 512px et peuvent être réduits selon le contexte:
 * - size="lg" : 128px (batailles, détails)
 * - size="md" : 64px (liste des flottes)
 * - size="sm" : 32px (icônes, menus)
 * - size="xs" : 24px (mini icônes)
 */

import './ShipSprite.css';

// Mapping des types de vaisseaux vers les dossiers de sprites
const SHIP_TYPE_FOLDERS: Record<string, string> = {
  fighter: 'fighter',
  scout: 'scout',
  colony: 'colony',
  satellite: 'satellite',
  tanker: 'tanker',
  battleship: 'battleship',
  decoy: 'decoy',
  bio: 'bio',
};

// Tailles en pixels
const SIZES = {
  xs: 24,
  sm: 32,
  md: 64,
  lg: 128,
  xl: 192,
  full: 512,
};

interface ShipSpriteProps {
  type: string;
  level?: number; // 1-4, correspond au niveau technologique
  size?: keyof typeof SIZES;
  className?: string;
  animated?: boolean; // Animation de vol
}

function ShipSprite({
  type,
  level = 1,
  size = 'md',
  className = '',
  animated = false,
}: ShipSpriteProps) {
  const folder = SHIP_TYPE_FOLDERS[type] || 'fighter';
  const levelNum = Math.min(4, Math.max(1, level));
  const src = `/ships/${folder}/ship-0${levelNum}.png`;
  const pixelSize = SIZES[size];

  return (
    <img
      src={src}
      alt={`${type} niveau ${levelNum}`}
      className={`ship-sprite ship-sprite-${size} ${animated ? 'ship-animated' : ''} ${className}`}
      style={{
        width: pixelSize,
        height: pixelSize,
      }}
      draggable={false}
    />
  );
}

// Composant pour afficher une grille de vaisseaux (composition de flotte)
interface ShipGridProps {
  ships: Record<string, number>; // { fighter: 5, battleship: 2, ... }
  techLevel?: number;
  maxDisplay?: number;
  size?: keyof typeof SIZES;
}

export function ShipGrid({ ships, techLevel = 1, maxDisplay = 12, size = 'sm' }: ShipGridProps) {
  const shipList: { type: string; count: number }[] = [];

  Object.entries(ships).forEach(([type, count]) => {
    if (count > 0) {
      shipList.push({ type, count });
    }
  });

  // Trier par nombre décroissant
  shipList.sort((a, b) => b.count - a.count);

  let displayed = 0;
  const elements: JSX.Element[] = [];

  for (const { type, count } of shipList) {
    const toShow = Math.min(count, maxDisplay - displayed);
    for (let i = 0; i < toShow && displayed < maxDisplay; i++) {
      elements.push(
        <ShipSprite
          key={`${type}-${i}`}
          type={type}
          level={techLevel}
          size={size}
        />
      );
      displayed++;
    }
    if (displayed >= maxDisplay) break;
  }

  const remaining = Object.values(ships).reduce((a, b) => a + b, 0) - displayed;

  return (
    <div className="ship-grid">
      {elements}
      {remaining > 0 && (
        <span className="ship-grid-overflow">+{remaining}</span>
      )}
    </div>
  );
}

// Galerie de tous les types de vaisseaux (pour debug/showcase)
export function ShipGallery() {
  const types = Object.keys(SHIP_TYPE_FOLDERS);
  const levels = [1, 2, 3, 4];

  return (
    <div className="ship-gallery">
      <h2>Galerie des Vaisseaux LEGO</h2>
      <div className="gallery-grid">
        {types.map(type => (
          <div key={type} className="gallery-row">
            <h3>{type.charAt(0).toUpperCase() + type.slice(1)}</h3>
            <div className="gallery-levels">
              {levels.map(level => (
                <div key={level} className="gallery-item">
                  <ShipSprite type={type} level={level} size="lg" />
                  <span className="gallery-label">Nv.{level}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ShipSprite;
