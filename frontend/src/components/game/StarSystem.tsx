import type { Star } from '../../hooks/useGameState';
import PlanetMarker from './PlanetMarker';

interface StarSystemProps {
  star: Star;
  isSelected: boolean;
  myPlayerId: number;
  zoom: number;
  getPlayerColor: (playerId: number | null) => string;
  onClick: () => void;
}

function StarSystem({
  star,
  isSelected,
  myPlayerId,
  zoom,
  getPlayerColor,
  onClick,
}: StarSystemProps) {
  const hasOwnedPlanet = star.planets.some((p) => p.owner_id === myPlayerId);
  const hasEnemyPlanet = star.planets.some(
    (p) => p.owner_id && p.owner_id !== myPlayerId
  );

  // Taille de l'étoile selon sélection
  const starRadius = isSelected ? 3 : 2;
  const glowRadius = isSelected ? 5 : 4;

  return (
    <g
      className={`star-system ${isSelected ? 'selected' : ''}`}
      onClick={onClick}
      style={{ cursor: 'pointer' }}
    >
      {/* Halo de l'étoile */}
      <circle
        cx={star.x}
        cy={star.y}
        r={glowRadius}
        fill={star.is_nova ? '#ff4444' : '#ffdd44'}
        opacity="0.2"
        filter="url(#glow)"
      />

      {/* Coeur de l'étoile */}
      <circle
        cx={star.x}
        cy={star.y}
        r={starRadius}
        fill={star.is_nova ? '#ff0000' : '#ffffff'}
        className="star-core"
      />

      {/* Indicateur de possession */}
      {hasOwnedPlanet && (
        <circle
          cx={star.x}
          cy={star.y}
          r={6}
          fill="none"
          stroke={getPlayerColor(myPlayerId)}
          strokeWidth="1.5"
          opacity="0.8"
        />
      )}
      {hasEnemyPlanet && !hasOwnedPlanet && (
        <circle
          cx={star.x}
          cy={star.y}
          r={6}
          fill="none"
          stroke="#ff4444"
          strokeWidth="0.5"
          strokeDasharray="2,2"
          opacity="0.6"
        />
      )}

      {/* Marqueurs de planètes (visibles à zoom élevé) */}
      {zoom >= 1.2 && star.planets.map((planet, index) => {
        const angle = (index / star.planets.length) * Math.PI * 2 - Math.PI / 2;
        const orbitRadius = 8 + index * 3;
        const px = star.x + Math.cos(angle) * orbitRadius;
        const py = star.y + Math.sin(angle) * orbitRadius;

        return (
          <PlanetMarker
            key={planet.id}
            planet={planet}
            x={px}
            y={py}
            myPlayerId={myPlayerId}
            getPlayerColor={getPlayerColor}
            showDetails={zoom >= 1.8}
          />
        );
      })}

      {/* Nom de l'étoile (visible à zoom moyen+) */}
      {zoom >= 1.0 && (
        <text
          x={star.x}
          y={star.y + (zoom >= 1.2 ? 18 : 10)}
          textAnchor="middle"
          fill="#888"
          fontSize={zoom >= 1.5 ? 3 : 4}
          className="star-name"
        >
          {star.name}
        </text>
      )}

      {/* Compteur de planètes (visible à zoom faible) */}
      {zoom < 1.0 && star.planets.length > 0 && (
        <text
          x={star.x + 4}
          y={star.y - 2}
          fill="#666"
          fontSize="3"
        >
          {star.planets.length}
        </text>
      )}
    </g>
  );
}

export default StarSystem;
