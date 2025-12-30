// Icônes pixelisées style 8-bit / Mistral AI
// Chaque icône utilise une grille de pixels pour un rendu rétro

interface IconProps {
  size?: number;
  color?: string;
  className?: string;
}

// Fonction helper pour créer des pixels
const Pixel = ({ x, y, size = 2, color = 'currentColor' }: { x: number; y: number; size?: number; color?: string }) => (
  <rect x={x * size} y={y * size} width={size} height={size} fill={color} />
);

// Grille 8x8 pour les icônes
const GRID = 8;

export function PixelRocket({ size = 24, color = 'currentColor', className }: IconProps) {
  const s = size / (GRID * 2); // taille d'un pixel
  return (
    <svg width={size} height={size} viewBox={`0 0 ${GRID * 2} ${GRID * 2}`} className={className} fill={color}>
      {/* Fusée pixelisée */}
      <Pixel x={7} y={1} size={1} color={color} />
      <Pixel x={6} y={2} size={1} color={color} />
      <Pixel x={7} y={2} size={1} color={color} />
      <Pixel x={8} y={2} size={1} color={color} />
      <Pixel x={6} y={3} size={1} color={color} />
      <Pixel x={7} y={3} size={1} color={color} />
      <Pixel x={8} y={3} size={1} color={color} />
      <Pixel x={5} y={4} size={1} color={color} />
      <Pixel x={6} y={4} size={1} color={color} />
      <Pixel x={7} y={4} size={1} color={color} />
      <Pixel x={8} y={4} size={1} color={color} />
      <Pixel x={9} y={4} size={1} color={color} />
      <Pixel x={5} y={5} size={1} color={color} />
      <Pixel x={6} y={5} size={1} color={color} />
      <Pixel x={7} y={5} size={1} color={color} />
      <Pixel x={8} y={5} size={1} color={color} />
      <Pixel x={9} y={5} size={1} color={color} />
      <Pixel x={4} y={6} size={1} color={color} />
      <Pixel x={6} y={6} size={1} color={color} />
      <Pixel x={7} y={6} size={1} color={color} />
      <Pixel x={8} y={6} size={1} color={color} />
      <Pixel x={10} y={6} size={1} color={color} />
      <Pixel x={4} y={7} size={1} color={color} />
      <Pixel x={6} y={7} size={1} color={color} />
      <Pixel x={7} y={7} size={1} color={color} />
      <Pixel x={8} y={7} size={1} color={color} />
      <Pixel x={10} y={7} size={1} color={color} />
      <Pixel x={3} y={8} size={1} color={color} />
      <Pixel x={5} y={8} size={1} color={color} />
      <Pixel x={9} y={8} size={1} color={color} />
      <Pixel x={11} y={8} size={1} color={color} />
      <Pixel x={6} y={9} size={1} color={color} />
      <Pixel x={8} y={9} size={1} color={color} />
      <Pixel x={5} y={10} size={1} color={color} />
      <Pixel x={7} y={10} size={1} color={color} />
      <Pixel x={9} y={10} size={1} color={color} />
      <Pixel x={6} y={11} size={1} color={color} />
      <Pixel x={7} y={11} size={1} color={color} />
      <Pixel x={8} y={11} size={1} color={color} />
      <Pixel x={7} y={12} size={1} color={color} />
    </svg>
  );
}

export function PixelUsers({ size = 24, color = 'currentColor', className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" className={className} fill={color}>
      {/* Personnage 1 */}
      <rect x="3" y="2" width="2" height="2" />
      <rect x="2" y="4" width="4" height="1" />
      <rect x="3" y="5" width="2" height="3" />
      <rect x="2" y="8" width="1" height="2" />
      <rect x="5" y="8" width="1" height="2" />
      <rect x="2" y="10" width="4" height="1" />
      {/* Personnage 2 */}
      <rect x="11" y="2" width="2" height="2" />
      <rect x="10" y="4" width="4" height="1" />
      <rect x="11" y="5" width="2" height="3" />
      <rect x="10" y="8" width="1" height="2" />
      <rect x="13" y="8" width="1" height="2" />
      <rect x="10" y="10" width="4" height="1" />
      {/* Personnage 3 (centre, devant) */}
      <rect x="7" y="5" width="2" height="2" />
      <rect x="6" y="7" width="4" height="1" />
      <rect x="7" y="8" width="2" height="3" />
      <rect x="6" y="11" width="1" height="2" />
      <rect x="9" y="11" width="1" height="2" />
      <rect x="6" y="13" width="4" height="1" />
    </svg>
  );
}

export function PixelChart({ size = 24, color = 'currentColor', className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" className={className} fill={color}>
      {/* Barres du graphique */}
      <rect x="2" y="10" width="3" height="4" />
      <rect x="6" y="6" width="3" height="8" />
      <rect x="10" y="2" width="3" height="12" />
      {/* Axe X */}
      <rect x="1" y="14" width="14" height="1" />
      {/* Axe Y */}
      <rect x="1" y="1" width="1" height="14" />
    </svg>
  );
}

export function PixelBook({ size = 24, color = 'currentColor', className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" className={className} fill={color}>
      {/* Livre ouvert */}
      <rect x="1" y="3" width="6" height="1" />
      <rect x="1" y="4" width="1" height="9" />
      <rect x="6" y="4" width="1" height="9" />
      <rect x="1" y="13" width="6" height="1" />
      {/* Page gauche - lignes */}
      <rect x="2" y="5" width="4" height="1" />
      <rect x="2" y="7" width="4" height="1" />
      <rect x="2" y="9" width="3" height="1" />
      <rect x="2" y="11" width="4" height="1" />
      {/* Partie droite */}
      <rect x="9" y="3" width="6" height="1" />
      <rect x="9" y="4" width="1" height="9" />
      <rect x="14" y="4" width="1" height="9" />
      <rect x="9" y="13" width="6" height="1" />
      {/* Page droite - lignes */}
      <rect x="10" y="5" width="4" height="1" />
      <rect x="10" y="7" width="4" height="1" />
      <rect x="10" y="9" width="3" height="1" />
      <rect x="10" y="11" width="4" height="1" />
      {/* Reliure centrale */}
      <rect x="7" y="2" width="2" height="12" />
    </svg>
  );
}

export function PixelUser({ size = 24, color = 'currentColor', className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" className={className} fill={color}>
      {/* Tête */}
      <rect x="6" y="2" width="4" height="4" />
      {/* Cou */}
      <rect x="7" y="6" width="2" height="1" />
      {/* Corps */}
      <rect x="4" y="7" width="8" height="1" />
      <rect x="3" y="8" width="10" height="1" />
      <rect x="3" y="9" width="10" height="1" />
      <rect x="4" y="10" width="8" height="1" />
      <rect x="5" y="11" width="6" height="1" />
      <rect x="5" y="12" width="2" height="2" />
      <rect x="9" y="12" width="2" height="2" />
    </svg>
  );
}

export function PixelLogout({ size = 24, color = 'currentColor', className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" className={className} fill={color}>
      {/* Porte */}
      <rect x="2" y="2" width="1" height="12" />
      <rect x="2" y="2" width="5" height="1" />
      <rect x="2" y="13" width="5" height="1" />
      <rect x="6" y="2" width="1" height="5" />
      <rect x="6" y="9" width="1" height="5" />
      {/* Flèche sortie */}
      <rect x="8" y="7" width="6" height="2" />
      <rect x="11" y="5" width="2" height="2" />
      <rect x="11" y="9" width="2" height="2" />
      <rect x="13" y="6" width="1" height="4" />
    </svg>
  );
}

export function PixelChevron({ size = 12, color = 'currentColor', className, direction = 'down' }: IconProps & { direction?: 'up' | 'down' | 'left' | 'right' }) {
  const rotation = {
    down: 0,
    up: 180,
    right: -90,
    left: 90,
  }[direction];

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 12 12"
      className={className}
      fill={color}
      style={{ transform: `rotate(${rotation}deg)` }}
    >
      <rect x="2" y="4" width="2" height="2" />
      <rect x="4" y="6" width="2" height="2" />
      <rect x="6" y="6" width="2" height="2" />
      <rect x="8" y="4" width="2" height="2" />
    </svg>
  );
}

export function PixelStar({ size = 24, color = 'currentColor', className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" className={className} fill={color}>
      <rect x="7" y="1" width="2" height="2" />
      <rect x="7" y="3" width="2" height="2" />
      <rect x="5" y="5" width="6" height="2" />
      <rect x="1" y="5" width="4" height="2" />
      <rect x="11" y="5" width="4" height="2" />
      <rect x="3" y="7" width="10" height="2" />
      <rect x="4" y="9" width="8" height="2" />
      <rect x="3" y="11" width="3" height="2" />
      <rect x="10" y="11" width="3" height="2" />
      <rect x="2" y="13" width="2" height="2" />
      <rect x="12" y="13" width="2" height="2" />
    </svg>
  );
}

export function PixelPlanet({ size = 24, color = 'currentColor', className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" className={className} fill={color}>
      {/* Planète */}
      <rect x="5" y="2" width="6" height="2" />
      <rect x="3" y="4" width="10" height="2" />
      <rect x="2" y="6" width="12" height="4" />
      <rect x="3" y="10" width="10" height="2" />
      <rect x="5" y="12" width="6" height="2" />
      {/* Anneau (effet creux) */}
      <rect x="1" y="7" width="1" height="2" fill="none" stroke={color} strokeWidth="0.5" />
      <rect x="14" y="7" width="1" height="2" fill="none" stroke={color} strokeWidth="0.5" />
    </svg>
  );
}

export function PixelSword({ size = 24, color = 'currentColor', className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" className={className} fill={color}>
      {/* Lame */}
      <rect x="12" y="1" width="2" height="2" />
      <rect x="10" y="3" width="2" height="2" />
      <rect x="8" y="5" width="2" height="2" />
      <rect x="6" y="7" width="2" height="2" />
      {/* Garde */}
      <rect x="3" y="9" width="6" height="2" />
      {/* Poignée */}
      <rect x="4" y="11" width="2" height="3" />
      <rect x="3" y="14" width="4" height="1" />
    </svg>
  );
}

export function PixelCrown({ size = 24, color = 'currentColor', className }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" className={className} fill={color}>
      {/* Pointes de la couronne */}
      <rect x="2" y="3" width="2" height="2" />
      <rect x="7" y="2" width="2" height="2" />
      <rect x="12" y="3" width="2" height="2" />
      {/* Corps de la couronne */}
      <rect x="2" y="5" width="12" height="2" />
      <rect x="2" y="7" width="12" height="4" />
      {/* Base */}
      <rect x="1" y="11" width="14" height="2" />
      {/* Joyaux */}
      <rect x="4" y="8" width="2" height="2" fill="var(--orange-dark, #e85a1e)" />
      <rect x="10" y="8" width="2" height="2" fill="var(--orange-dark, #e85a1e)" />
    </svg>
  );
}
