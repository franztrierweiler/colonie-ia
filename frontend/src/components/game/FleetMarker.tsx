import type { Fleet } from '../../hooks/useGameState';

interface FleetMarkerProps {
  fleet: Fleet;
  x: number;
  y: number;
  color: string;
  isMine: boolean;
  zoom: number;
  onClick: () => void;
}

function FleetMarker({
  fleet,
  x,
  y,
  color,
  isMine,
  zoom,
  onClick,
}: FleetMarkerProps) {
  // Position du marqueur (décalé par rapport à l'étoile)
  const offsetX = 6;
  const offsetY = -2;
  const markerX = x + offsetX;
  const markerY = y + offsetY;

  return (
    <g
      className={`fleet-marker ${isMine ? 'mine' : 'enemy'}`}
      onClick={(e) => {
        e.stopPropagation();
        onClick();
      }}
      style={{ cursor: 'pointer' }}
    >
      {/* Icône vaisseau (triangle/flèche) */}
      <polygon
        points={`
          ${markerX},${markerY - 2}
          ${markerX + 3},${markerY}
          ${markerX},${markerY + 2}
          ${markerX + 1},${markerY}
        `}
        fill={color}
        stroke={isMine ? '#fff' : 'none'}
        strokeWidth="0.3"
        className="fleet-icon"
      />

      {/* Nombre de vaisseaux */}
      {zoom >= 0.8 && (
        <text
          x={markerX + 5}
          y={markerY + 1}
          fill={color}
          fontSize="3"
          fontWeight="bold"
        >
          {fleet.ship_count}
        </text>
      )}

      {/* Nom de la flotte (zoom élevé) */}
      {zoom >= 1.5 && isMine && (
        <text
          x={markerX}
          y={markerY + 6}
          fill="#888"
          fontSize="2"
        >
          {fleet.name}
        </text>
      )}

      {/* Indicateur flotte sélectionnée ou survolée */}
      <circle
        cx={markerX + 1}
        cy={markerY}
        r={4}
        fill="none"
        stroke={color}
        strokeWidth="0.3"
        opacity="0"
        className="fleet-highlight"
      />
    </g>
  );
}

export default FleetMarker;
