/**
 * ShipCountBadge - Pastille affichant le nombre de vaisseaux stationnés
 * Cliquable pour ouvrir la modale de sélection
 */

interface ShipCountBadgeProps {
  x: number;
  y: number;
  count: number;
  color: string;
  onClick: () => void;
}

function ShipCountBadge({ x, y, count, color, onClick }: ShipCountBadgeProps) {
  if (count <= 0) return null;

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onClick();
  };

  // Taille du badge selon le nombre de vaisseaux
  const radius = count >= 100 ? 5 : count >= 10 ? 4 : 3;
  const fontSize = count >= 100 ? 3 : count >= 10 ? 3.5 : 4;

  return (
    <g
      className="ship-count-badge"
      onClick={handleClick}
      style={{ cursor: 'pointer' }}
    >
      {/* Cercle de fond */}
      <circle
        cx={x}
        cy={y}
        r={radius + 1}
        fill="#000"
        opacity="0.6"
      />
      {/* Cercle coloré (sans contour) */}
      <circle
        cx={x}
        cy={y}
        r={radius}
        fill={color}
      />
      {/* Nombre de vaisseaux */}
      <text
        x={x}
        y={y + 0.5}
        textAnchor="middle"
        dominantBaseline="middle"
        fill="#fff"
        fontSize={fontSize}
        fontWeight="bold"
        style={{ pointerEvents: 'none' }}
      >
        {count}
      </text>
    </g>
  );
}

export default ShipCountBadge;
