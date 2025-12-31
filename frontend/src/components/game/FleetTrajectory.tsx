interface FleetTrajectoryProps {
  fromX: number;
  fromY: number;
  toX: number;
  toY: number;
  color: string;
  isMine: boolean;
}

function FleetTrajectory({
  fromX,
  fromY,
  toX,
  toY,
  color,
  isMine,
}: FleetTrajectoryProps) {
  // Calcul de la distance et du nombre de segments (1 par tour estimé)
  const dx = toX - fromX;
  const dy = toY - fromY;
  const distance = Math.sqrt(dx * dx + dy * dy);
  const segments = Math.max(2, Math.ceil(distance / 10)); // ~10 unités par tour

  // Points intermédiaires pour les marqueurs de tour
  const turnMarkers = [];
  for (let i = 1; i < segments; i++) {
    const t = i / segments;
    turnMarkers.push({
      x: fromX + dx * t,
      y: fromY + dy * t,
    });
  }

  return (
    <g className="fleet-trajectory">
      {/* Ligne de trajectoire */}
      <line
        x1={fromX}
        y1={fromY}
        x2={toX}
        y2={toY}
        stroke={color}
        strokeWidth={isMine ? 0.8 : 0.5}
        strokeDasharray={isMine ? '3,2' : '2,3'}
        opacity={isMine ? 0.7 : 0.4}
      />

      {/* Marqueurs de tour */}
      {isMine && turnMarkers.map((point, index) => (
        <circle
          key={index}
          cx={point.x}
          cy={point.y}
          r={1}
          fill={color}
          opacity="0.6"
        />
      ))}

      {/* Point de destination */}
      <circle
        cx={toX}
        cy={toY}
        r={isMine ? 2.5 : 1.5}
        fill="none"
        stroke={color}
        strokeWidth={isMine ? 1 : 0.5}
        opacity={isMine ? 0.8 : 0.5}
      />

      {/* Flèche de direction */}
      {isMine && (
        <polygon
          points={calculateArrowPoints(fromX, fromY, toX, toY)}
          fill={color}
          opacity="0.8"
        />
      )}
    </g>
  );
}

// Calcule les points du triangle de la flèche
function calculateArrowPoints(
  fromX: number,
  fromY: number,
  toX: number,
  toY: number
): string {
  const dx = toX - fromX;
  const dy = toY - fromY;
  const length = Math.sqrt(dx * dx + dy * dy);

  if (length === 0) return '';

  // Normaliser le vecteur
  const nx = dx / length;
  const ny = dy / length;

  // Position de la flèche (80% du chemin)
  const arrowPos = 0.8;
  const ax = fromX + dx * arrowPos;
  const ay = fromY + dy * arrowPos;

  // Taille de la flèche
  const arrowSize = 2;

  // Points du triangle
  const tipX = ax + nx * arrowSize;
  const tipY = ay + ny * arrowSize;
  const leftX = ax - ny * arrowSize * 0.5;
  const leftY = ay + nx * arrowSize * 0.5;
  const rightX = ax + ny * arrowSize * 0.5;
  const rightY = ay - nx * arrowSize * 0.5;

  return `${tipX},${tipY} ${leftX},${leftY} ${rightX},${rightY}`;
}

export default FleetTrajectory;
