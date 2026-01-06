import type { Fleet } from '../../hooks/useGameState';

interface FleetMarkerProps {
  fleet: Fleet;
  x: number;
  y: number;
  color: string;
  isMine: boolean;
  zoom: number;
  isDragging?: boolean;
  onClick: () => void;
  onDragStart?: () => void;
}

function FleetMarker({
  fleet,
  x,
  y,
  color,
  isMine,
  zoom,
  isDragging = false,
  onClick,
  onDragStart,
}: FleetMarkerProps) {
  // Position du marqueur (décalé par rapport à la planète)
  const offsetX = 12;
  const offsetY = -4;
  const markerX = x + offsetX;
  const markerY = y + offsetY;

  // Taille du marqueur (plus grand = plus facile à attraper)
  const size = 8;

  const handleMouseDown = (e: React.MouseEvent) => {
    if (isMine && onDragStart) {
      e.stopPropagation();
      e.preventDefault();
      onDragStart();
    }
  };

  return (
    <g
      className={`fleet-marker ${isMine ? 'mine' : 'enemy'} ${isDragging ? 'dragging' : ''}`}
      onClick={(e) => {
        e.stopPropagation();
        onClick();
      }}
      onMouseDown={handleMouseDown}
      style={{ cursor: isMine ? 'grab' : 'pointer' }}
    >
      {/* Zone de clic invisible plus grande */}
      <rect
        x={markerX - size/2}
        y={markerY - size/2}
        width={size * 2}
        height={size}
        fill="transparent"
      />

      {/* Icône vaisseau (triangle/flèche) - plus grand */}
      <polygon
        points={`
          ${markerX},${markerY - size/2}
          ${markerX + size},${markerY}
          ${markerX},${markerY + size/2}
          ${markerX + size/3},${markerY}
        `}
        fill={color}
        stroke={isMine ? '#fff' : '#333'}
        strokeWidth="0.5"
        className="fleet-icon"
      />

      {/* Nombre de vaisseaux */}
      <text
        x={markerX + size + 2}
        y={markerY + 2}
        fill={color}
        fontSize="5"
        fontWeight="bold"
        stroke="#000"
        strokeWidth="0.3"
      >
        {fleet.ship_count}
      </text>

      {/* Nom de la flotte */}
      {zoom >= 1.0 && isMine && (
        <text
          x={markerX}
          y={markerY + size + 4}
          fill="#aaa"
          fontSize="3"
        >
          {fleet.name}
        </text>
      )}

      {/* Indicateur drag actif */}
      {isDragging && (
        <circle
          cx={markerX + size/2}
          cy={markerY}
          r={size}
          fill="none"
          stroke="#4ade80"
          strokeWidth="1"
          strokeDasharray="2 1"
        />
      )}
    </g>
  );
}

export default FleetMarker;
