import type { Planet } from '../../hooks/useGameState';
import ShipCountBadge from './ShipCountBadge';
import './PlanetMarker.css';

interface PlanetMarkerProps {
  planet: Planet;
  isSelected: boolean;
  myPlayerId: number;
  zoom: number;
  getPlayerColor: (playerId: number | null) => string;
  onClick: () => void;
  canDrag?: boolean;
  onDragStart?: () => void;
  stationedShipCount?: number;
  onShipBadgeClick?: () => void;
  // Indicateurs orbitaux
  hasSatellite?: boolean;
  hasShipsInConstruction?: boolean;
}

function PlanetMarker({
  planet,
  isSelected,
  myPlayerId,
  zoom,
  getPlayerColor,
  onClick,
  canDrag = false,
  onDragStart,
  stationedShipCount = 0,
  onShipBadgeClick,
  hasSatellite = false,
  hasShipsInConstruction = false,
}: PlanetMarkerProps) {
  const isOwned = planet.owner_id !== null;
  const isMine = planet.owner_id === myPlayerId;
  const isEnemy = isOwned && !isMine;
  const isUnexplored = planet.state === 'unexplored';
  const isHomePlanet = planet.is_home_planet;
  const ownerColor = getPlayerColor(planet.owner_id);

  // Type de planète et conditions
  const isGaseous = planet.texture_type === 'gas';
  const isHostile = !isUnexplored && (
    planet.texture_type === 'volcanic' ||
    planet.texture_type === 'ice' ||
    (planet.texture_type === 'barren' && planet.habitability < 0.2)
  );

  // Taille selon sélection
  const planetRadius = isSelected ? 6 : 5;
  const glowRadius = isSelected ? 8 : 7;

  // Rayons pour les orbites
  const satelliteOrbitRadius = planetRadius + 4;
  const constructionOrbitRadius = planetRadius + (hasSatellite ? 7 : 5);

  const getPlanetTexture = (): string => {
    if (isUnexplored) return '';
    const textureType = planet.texture_type || 'barren';
    const textureIdx = planet.texture_index || 1;
    const paddedIdx = String(textureIdx).padStart(3, '0');
    return `/planets/${textureType}/planet-${paddedIdx}.png`;
  };

  const planetTexture = getPlanetTexture();

  const getFallbackFill = () => {
    if (isUnexplored) return '#3a3a4a';
    switch (planet.texture_type) {
      case 'gas': return '#884422';
      case 'volcanic': return '#aa3300';
      case 'ice': return '#aaddff';
      case 'desert': return '#cc9966';
      case 'habitable': return '#2266aa';
      case 'barren':
      default: return '#888888';
    }
  };

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onClick();
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (canDrag && onDragStart) {
      e.preventDefault();
      onDragStart();
    }
  };

  return (
    <g
      className={`planet-marker ${isSelected ? 'selected' : ''} ${canDrag ? 'can-drag' : ''}`}
      onClick={handleClick}
      onMouseDown={handleMouseDown}
      style={{ cursor: canDrag ? 'grab' : 'pointer' }}
    >
      {/* Cercle bleu épais pulsant pour MA planète mère */}
      {isHomePlanet && isMine && (
        <circle
          cx={planet.x}
          cy={planet.y}
          r={planetRadius + 4}
          fill="none"
          stroke="#4488ff"
          strokeWidth="3"
          className="home-planet-ring"
        />
      )}

      {/* Halo pour planètes gazeuses hostiles */}
      {isHostile && isGaseous && (
        <circle
          cx={planet.x}
          cy={planet.y}
          r={planetRadius + 3}
          fill="none"
          stroke="#ff6644"
          strokeWidth="1.5"
          opacity="0.6"
          className="gaseous-halo"
        />
      )}

      {/* Halo de base */}
      {!(isHomePlanet && isMine) && (
        <circle
          cx={planet.x}
          cy={planet.y}
          r={glowRadius}
          fill={planet.is_nova ? '#ff4444' : getFallbackFill()}
          opacity="0.2"
          filter="url(#glow)"
        />
      )}

      {/* === INDICATEURS ORBITAUX === */}

      {/* Constellation de 9 micro-satellites répartis aléatoirement avec onde radar */}
      {hasSatellite && (() => {
        // Générateur pseudo-aléatoire basé sur l'ID de la planète
        const seed = planet.id * 137.5;
        const pseudoRandom = (i: number) => {
          const x = Math.sin(seed + i * 97.3) * 10000;
          return x - Math.floor(x);
        };
        // Période radar entre 5s (0.2Hz) et 20s (0.05Hz)
        const radarPeriod = 5 + (pseudoRandom(100) * 15);
        // Période de base pour l'orbite (20s)
        const baseOrbitPeriod = 20;

        return (
          <g>
            {/* 9 satellites avec vitesse variable selon distance */}
            {[0, 1, 2, 3, 4, 5, 6, 7, 8].map((i) => {
              const angle = pseudoRandom(i) * Math.PI * 2;
              const dist = 1 + pseudoRandom(i + 10) * 4; // rayon 1-5
              // Vitesse: +10% si proche, -10% si loin (dist 1-5 -> variation ±10%)
              const distFactor = (dist - 3) / 20; // -0.1 à +0.1
              const orbitPeriod = baseOrbitPeriod * (1 + distFactor);
              const driftDuration = 3 + pseudoRandom(i + 30) * 4;
              const driftDelay = pseudoRandom(i + 40) * 5;
              const orbitDelay = (planet.id % 20) + pseudoRandom(i + 50) * 2;

              return (
                <g
                  key={i}
                  className="satellite-orbit"
                  style={{
                    transformOrigin: `${planet.x}px ${planet.y}px`,
                    animationDuration: `${orbitPeriod}s`,
                    animationDelay: `${-orbitDelay}s`
                  }}
                >
                  <circle
                    cx={planet.x + satelliteOrbitRadius + Math.cos(angle) * dist}
                    cy={planet.y + Math.sin(angle) * dist}
                    r={0.25 + pseudoRandom(i + 20) * 0.1}
                    fill="#a0a0a0"
                    className="satellite-drift"
                    style={{
                      animationDuration: `${driftDuration}s`,
                      animationDelay: `${-driftDelay}s`
                    }}
                  />
                </g>
              );
            })}
            {/* Onde radar (tourne avec le groupe médian) */}
            <g
              className="satellite-orbit"
              style={{
                transformOrigin: `${planet.x}px ${planet.y}px`,
                animationDuration: `${baseOrbitPeriod}s`,
                animationDelay: `${-(planet.id % 20)}s`
              }}
            >
              <path
                d={`M${planet.x + satelliteOrbitRadius + 4},${planet.y - 2}
                    A3,3 0 0,1 ${planet.x + satelliteOrbitRadius + 4},${planet.y + 2}`}
                fill="none"
                stroke="#cccccc"
                strokeWidth="0.4"
                className="radar-wave-1"
                style={{ animationDuration: `${radarPeriod}s` }}
              />
              <path
                d={`M${planet.x + satelliteOrbitRadius + 5.5},${planet.y - 3}
                    A4.5,4.5 0 0,1 ${planet.x + satelliteOrbitRadius + 5.5},${planet.y + 3}`}
                fill="none"
                stroke="#aaaaaa"
                strokeWidth="0.3"
                className="radar-wave-2"
                style={{ animationDuration: `${radarPeriod}s` }}
              />
              <path
                d={`M${planet.x + satelliteOrbitRadius + 7},${planet.y - 4}
                    A6,6 0 0,1 ${planet.x + satelliteOrbitRadius + 7},${planet.y + 4}`}
                fill="none"
                stroke="#888888"
                strokeWidth="0.25"
                className="radar-wave-3"
                style={{ animationDuration: `${radarPeriod}s` }}
              />
            </g>
          </g>
        );
      })()}

      {/* Pastille construction jaune→rouge + arcs électriques (sous le badge vaisseaux) */}
      {hasShipsInConstruction && isMine && (
        (() => {
          // Position sous le badge vaisseaux
          const badgeX = planet.x + planetRadius + 4;
          const badgeY = planet.y - planetRadius + (stationedShipCount > 0 ? 8 : 0);
          const badgeRadius = 3;
          return (
            <g>
              {/* Cercle de fond */}
              <circle
                cx={badgeX}
                cy={badgeY}
                r={badgeRadius + 1}
                fill="#000"
                opacity="0.6"
              />
              {/* Pastille de construction animée (sans contour) */}
              <circle
                cx={badgeX}
                cy={badgeY}
                r={badgeRadius}
                className="construction-indicator"
              />
              {/* Arcs électriques */}
              <path
                d={`M${badgeX - 4},${badgeY - 2} L${badgeX - 2},${badgeY} L${badgeX - 5},${badgeY + 1}`}
                stroke="#88ffff"
                strokeWidth="0.5"
                fill="none"
                strokeDasharray="2,1"
                className="electric-arc-1"
              />
              <path
                d={`M${badgeX + 2},${badgeY - 4} L${badgeX},${badgeY - 2} L${badgeX + 3},${badgeY - 1}`}
                stroke="#ffff88"
                strokeWidth="0.5"
                fill="none"
                strokeDasharray="1.5,1"
                className="electric-arc-2"
              />
              <path
                d={`M${badgeX + 3},${badgeY + 2} L${badgeX + 1},${badgeY + 1} L${badgeX + 4},${badgeY + 3}`}
                stroke="#ffffff"
                strokeWidth="0.4"
                fill="none"
                strokeDasharray="1,1.5"
                className="electric-arc-3"
              />
            </g>
          );
        })()
      )}

      {/* ClipPath pour la texture */}
      <defs>
        <clipPath id={`planet-clip-${planet.id}`}>
          <circle cx={planet.x} cy={planet.y} r={planetRadius} />
        </clipPath>
      </defs>

      {/* Coeur de la planète */}
      {planet.is_nova ? (
        <circle
          cx={planet.x}
          cy={planet.y}
          r={planetRadius}
          fill="#ff0000"
          className="planet-core"
        />
      ) : isUnexplored ? (
        <circle
          cx={planet.x}
          cy={planet.y}
          r={planetRadius}
          fill="#555"
          stroke="#666"
          strokeWidth="0.5"
          className="planet-core"
        />
      ) : (
        <g clipPath={`url(#planet-clip-${planet.id})`}>
          <circle
            cx={planet.x}
            cy={planet.y}
            r={planetRadius}
            fill={getFallbackFill()}
          />
          <image
            href={planetTexture}
            x={planet.x - planetRadius}
            y={planet.y - planetRadius}
            width={planetRadius * 2}
            height={planetRadius * 2}
            preserveAspectRatio="xMidYMid slice"
            className="planet-core"
          />
          <ellipse
            cx={planet.x}
            cy={planet.y}
            rx={planetRadius * 0.4}
            ry={planetRadius * 1.2}
            fill="rgba(0,0,0,0.15)"
            className="planet-terminator"
          />
        </g>
      )}

      {/* Point d'interrogation pour planètes inexplorées */}
      {isUnexplored && (
        <text
          x={planet.x}
          y={planet.y + 1.2}
          textAnchor="middle"
          fill="#aaa"
          fontSize="5"
          fontWeight="bold"
          style={{ pointerEvents: 'none' }}
        >
          ?
        </text>
      )}

      {/* Cercle fin de possession - bleu pour joueur, couleur ennemi pour adversaires */}
      {isMine && !isHomePlanet && (
        <circle
          cx={planet.x}
          cy={planet.y}
          r={planetRadius + 3}
          fill="none"
          stroke="#4488ff"
          strokeWidth="0.1"
          opacity="0.7"
          className="ownership-ring"
        />
      )}
      {isEnemy && (
        <circle
          cx={planet.x}
          cy={planet.y}
          r={planetRadius + 3}
          fill="none"
          stroke={ownerColor}
          strokeWidth="0.1"
          opacity="0.7"
          className="ownership-ring"
        />
      )}

      {/* Nom de la planète */}
      {zoom >= 1.0 && (
        <text
          x={planet.x}
          y={planet.y + planetRadius + 3}
          textAnchor="middle"
          fill={isUnexplored ? '#666' : '#999'}
          fontSize="0.05"
          fontFamily="Courier, 'Courier New', monospace"
          className="planet-name"
          style={{ pointerEvents: 'none' }}
        >
          {planet.name}
        </text>
      )}

      {/* Détails (zoom élevé) */}
      {zoom >= 2.0 && !isUnexplored && (
        <g className="planet-details">
          <text
            x={planet.x}
            y={planet.y + planetRadius + 8}
            textAnchor="middle"
            fill="#666"
            fontSize={Math.max(1.2, 2.5 / zoom)}
            style={{ pointerEvents: 'none' }}
          >
            {Math.round(planet.current_temperature)}°C
          </text>
          {isMine && (
            <text
              x={planet.x}
              y={planet.y + planetRadius + 11}
              textAnchor="middle"
              fill="#888"
              fontSize={Math.max(1, 2 / zoom)}
              style={{ pointerEvents: 'none' }}
            >
              {(planet.population / 1000).toFixed(0)}k
            </text>
          )}
        </g>
      )}

      {/* Point rouge pour nova imminente */}
      {planet.nova_turn && !planet.is_nova && (
        <circle
          cx={planet.x + planetRadius + 2}
          cy={planet.y - planetRadius - 2}
          r={2}
          fill="#ff0000"
          className="danger-blink"
        />
      )}

      {/* Pastille de vaisseaux stationnés */}
      {isMine && stationedShipCount > 0 && onShipBadgeClick && (
        <ShipCountBadge
          x={planet.x + planetRadius + 4}
          y={planet.y - planetRadius}
          count={stationedShipCount}
          color={ownerColor}
          onClick={onShipBadgeClick}
        />
      )}
    </g>
  );
}

export default PlanetMarker;
