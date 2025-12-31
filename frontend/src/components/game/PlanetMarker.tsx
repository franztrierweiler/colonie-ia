import type { Planet } from '../../hooks/useGameState';

interface PlanetMarkerProps {
  planet: Planet;
  x: number;
  y: number;
  myPlayerId: number;
  getPlayerColor: (playerId: number | null) => string;
  showDetails: boolean;
}

function PlanetMarker({
  planet,
  x,
  y,
  myPlayerId,
  getPlayerColor,
  showDetails,
}: PlanetMarkerProps) {
  const isOwned = planet.owner_id !== null;
  const isMine = planet.owner_id === myPlayerId;
  const isUnexplored = planet.state === 'unexplored';
  const ownerColor = getPlayerColor(planet.owner_id);

  // Couleur de la planète selon température
  const getPlanetColor = () => {
    const temp = planet.current_temperature;
    if (temp < -20) return '#88ccff'; // Très froid - bleu
    if (temp < 10) return '#aaddff';  // Froid - bleu clair
    if (temp < 30) return '#44aa44';  // Tempéré - vert
    if (temp < 50) return '#ddaa44';  // Chaud - orange
    return '#ff6644';                  // Très chaud - rouge
  };

  return (
    <g className="planet-marker">
      {/* Planète */}
      <circle
        cx={x}
        cy={y}
        r={1.5}
        fill={isUnexplored ? '#444' : getPlanetColor()}
        stroke={isOwned ? ownerColor : 'none'}
        strokeWidth="0.5"
      />

      {/* Icône selon état */}
      {isUnexplored ? (
        // Point d'interrogation pour planètes inexplorées
        <text
          x={x}
          y={y + 0.8}
          textAnchor="middle"
          fill="#888"
          fontSize="2.5"
          fontWeight="bold"
        >
          ?
        </text>
      ) : isOwned ? (
        // Bicorne pour planètes possédées
        <g transform={`translate(${x - 1.5}, ${y - 3.5})`}>
          <path
            d="M0.5,2 L1.5,0 L2.5,2 L1.5,1.5 Z"
            fill={ownerColor}
            stroke={isMine ? '#fff' : 'none'}
            strokeWidth="0.2"
          />
          {/* Cocarde tricolore pour les planètes du joueur */}
          {isMine && (
            <circle cx="1.5" cy="1" r="0.4" fill="#fff" />
          )}
        </g>
      ) : null}

      {/* Détails (visibles à zoom très élevé) */}
      {showDetails && !isUnexplored && (
        <g className="planet-details">
          {/* Nom de la planète */}
          <text
            x={x}
            y={y + 4}
            textAnchor="middle"
            fill="#666"
            fontSize="1.8"
          >
            {planet.name.split(' ').pop()}
          </text>

          {/* Indicateurs pour planètes possédées */}
          {isMine && (
            <>
              {/* Population */}
              <text
                x={x}
                y={y + 6}
                textAnchor="middle"
                fill="#888"
                fontSize="1.5"
              >
                {(planet.population / 1000).toFixed(0)}k
              </text>
            </>
          )}
        </g>
      )}

      {/* Indicateur planète mère */}
      {planet.is_home_planet && (
        <circle
          cx={x}
          cy={y}
          r={3}
          fill="none"
          stroke={ownerColor}
          strokeWidth="0.3"
          strokeDasharray="1,1"
          opacity="0.5"
        />
      )}
    </g>
  );
}

export default PlanetMarker;
