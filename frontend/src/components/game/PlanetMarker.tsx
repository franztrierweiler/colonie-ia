import type { Planet } from '../../hooks/useGameState';

interface PlanetMarkerProps {
  planet: Planet;
  isSelected: boolean;
  myPlayerId: number;
  zoom: number;
  getPlayerColor: (playerId: number | null) => string;
  onClick: () => void;
}

function PlanetMarker({
  planet,
  isSelected,
  myPlayerId,
  zoom,
  getPlayerColor,
  onClick,
}: PlanetMarkerProps) {
  const isOwned = planet.owner_id !== null;
  const isMine = planet.owner_id === myPlayerId;
  const isEnemy = isOwned && !isMine;
  const isUnexplored = planet.state === 'unexplored';
  const isHomePlanet = planet.is_home_planet;
  const ownerColor = getPlayerColor(planet.owner_id);

  // Type de planète et conditions (pour affichage des halos)
  const isGaseous = planet.texture_type === 'gas';
  const isHostile = !isUnexplored && (
    planet.texture_type === 'volcanic' ||
    planet.texture_type === 'ice' ||
    (planet.texture_type === 'barren' && planet.habitability < 0.2)
  );

  // Taille selon sélection (plus grand pour voir les textures)
  const planetRadius = isSelected ? 6 : 5;
  const glowRadius = isSelected ? 8 : 7;

  // Construit le chemin de texture à partir des valeurs stockées en base
  const getPlanetTexture = (): string => {
    // Planète inexplorée = pas de texture (gris uniforme)
    if (isUnexplored) return '';

    // Utiliser les valeurs stockées en base de données
    const textureType = planet.texture_type || 'barren';
    const textureIdx = planet.texture_index || 1;
    const paddedIdx = String(textureIdx).padStart(3, '0');

    return `/planets/${textureType}/planet-${paddedIdx}.png`;
  };

  const planetTexture = getPlanetTexture();

  // Fallback couleur selon le type de texture stocké
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

  return (
    <g
      className={`planet-marker ${isSelected ? 'selected' : ''}`}
      onClick={handleClick}
      onMouseDown={(e) => e.stopPropagation()}
      style={{ cursor: 'pointer' }}
    >
      {/* Halo bleu animé pour MA planète mère uniquement */}
      {isHomePlanet && isMine && (
        <>
          <circle
            cx={planet.x}
            cy={planet.y}
            r={planetRadius + 5}
            fill="none"
            stroke="#66aaff"
            strokeWidth="2"
            opacity="0.7"
            className="home-planet-halo-inner"
          />
          <circle
            cx={planet.x}
            cy={planet.y}
            r={planetRadius + 8}
            fill="none"
            stroke="#4488ff"
            strokeWidth="1.5"
            opacity="0.5"
            className="home-planet-halo-outer"
          />
        </>
      )}

      {/* Halo animé orange-rouge pour planètes gazeuses hostiles */}
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

      {/* Halo de sélection ou de base (pas pour ma planète mère qui a son halo bleu) */}
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

      {/* ClipPath pour découpage circulaire de la texture */}
      <defs>
        <clipPath id={`planet-clip-${planet.id}`}>
          <circle cx={planet.x} cy={planet.y} r={planetRadius} />
        </clipPath>
      </defs>

      {/* Coeur de la planète avec texture */}
      {planet.is_nova ? (
        <circle
          cx={planet.x}
          cy={planet.y}
          r={planetRadius}
          fill="#ff0000"
          className="planet-core"
        />
      ) : isUnexplored ? (
        /* Planète non explorée = cercle gris uniforme */
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
          {/* Cercle de fond (fallback) */}
          <circle
            cx={planet.x}
            cy={planet.y}
            r={planetRadius}
            fill={getFallbackFill()}
          />
          {/* Image de texture */}
          <image
            href={planetTexture}
            x={planet.x - planetRadius}
            y={planet.y - planetRadius}
            width={planetRadius * 2}
            height={planetRadius * 2}
            preserveAspectRatio="xMidYMid slice"
            className="planet-core"
          />
          {/* Effet d'auto-rotation (ombre qui traverse la surface) */}
          <ellipse
            cx={planet.x}
            cy={planet.y}
            rx={planetRadius * 0.4}
            ry={planetRadius * 1.2}
            fill="rgba(0,0,0,0.15)"
            className="planet-terminator"
            style={{
              ['--planet-x' as string]: `${planet.x}px`,
              ['--planet-radius' as string]: `${planetRadius}px`,
            }}
          />
        </g>
      )}

      {/* Point d'interrogation pour planètes inexplorées - toujours visible */}
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

      {/* Indicateur de possession - cercle */}
      {isMine && !isHomePlanet && (
        <circle
          cx={planet.x}
          cy={planet.y}
          r={planetRadius + 3}
          fill="none"
          stroke={ownerColor}
          strokeWidth="1.5"
          opacity="0.8"
        />
      )}
      {isEnemy && (
        <circle
          cx={planet.x}
          cy={planet.y}
          r={planetRadius + 3}
          fill="none"
          stroke="#ff4444"
          strokeWidth="0.5"
          strokeDasharray="2,2"
          opacity="0.6"
        />
      )}

      {/* Bicorne 3D pour planètes possédées (toujours visible) */}
      {isOwned && !isUnexplored && (
        <g transform={`translate(${planet.x}, ${planet.y - planetRadius * 0.6})`}>
          {/* Ombre du bicorne sur la planète */}
          <ellipse
            cx="0"
            cy={planetRadius * 0.15}
            rx="3"
            ry="1"
            fill="rgba(0,0,0,0.3)"
          />

          {isMine ? (
            /* Bicorne tricolore bleu-blanc-rouge pour le joueur */
            <g transform="translate(-4, -5)">
              {/* Ombre portée du bicorne */}
              <path
                d="M0.5,5.5 L4,0.5 L7.5,5.5 L4,4.5 Z"
                fill="rgba(0,0,0,0.2)"
                transform="translate(0.3, 0.3)"
              />
              {/* Corps du bicorne - dégradé pour effet 3D */}
              <defs>
                <linearGradient id={`bicorne-grad-${planet.id}`} x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="#ffffff" />
                  <stop offset="100%" stopColor="#cccccc" />
                </linearGradient>
              </defs>
              <path
                d="M0.5,5 L4,0 L7.5,5 L4,4 Z"
                fill={`url(#bicorne-grad-${planet.id})`}
                stroke="#333"
                strokeWidth="0.3"
              />
              {/* Bande bleue (gauche) avec ombre */}
              <path
                d="M0.5,5 L2.2,1.8 L2.6,2.3 L1.3,5 Z"
                fill="#0055a4"
              />
              <path
                d="M0.5,5 L2.2,1.8 L2.4,2 L1.1,5 Z"
                fill="#003d7a"
              />
              {/* Bande rouge (droite) avec ombre */}
              <path
                d="M7.5,5 L5.8,1.8 L5.4,2.3 L6.7,5 Z"
                fill="#ef4135"
              />
              <path
                d="M7.5,5 L5.8,1.8 L5.6,2 L6.9,5 Z"
                fill="#cc2a20"
              />
              {/* Rebord inférieur du bicorne (effet 3D) */}
              <path
                d="M0.5,5 L4,4 L7.5,5 L4,5.3 Z"
                fill="#222"
              />
              {/* Cocarde tricolore en relief */}
              <circle cx="4" cy="2.5" r="0.9" fill="#003d7a" />
              <circle cx="4" cy="2.5" r="0.7" fill="#0055a4" />
              <circle cx="4" cy="2.5" r="0.5" fill="#ffffff" />
              <circle cx="4" cy="2.5" r="0.25" fill="#ef4135" />
            </g>
          ) : (
            /* Bicorne de la couleur de l'ennemi en 3D */
            <g transform="translate(-4, -5)">
              {/* Ombre portée */}
              <path
                d="M0.5,5.5 L4,0.5 L7.5,5.5 L4,4.5 Z"
                fill="rgba(0,0,0,0.2)"
                transform="translate(0.3, 0.3)"
              />
              {/* Corps du bicorne avec dégradé */}
              <defs>
                <linearGradient id={`bicorne-enemy-grad-${planet.id}`} x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor={ownerColor} />
                  <stop offset="100%" stopColor="#333" />
                </linearGradient>
              </defs>
              <path
                d="M0.5,5 L4,0 L7.5,5 L4,4 Z"
                fill={`url(#bicorne-enemy-grad-${planet.id})`}
                stroke="#111"
                strokeWidth="0.3"
              />
              {/* Rebord inférieur */}
              <path
                d="M0.5,5 L4,4 L7.5,5 L4,5.3 Z"
                fill="#111"
              />
              {/* Insigne ennemi */}
              <circle cx="4" cy="2.5" r="0.6" fill="#111" />
              <circle cx="4" cy="2.5" r="0.35" fill="#333" />
            </g>
          )}
        </g>
      )}

      {/* Nom de la planète - sous la planète, taille fixe, visible à partir de 1:1 */}
      {/* TODO: revoir la méthode d'affichage des noms de planètes */}
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

      {/* Détails (visibles à zoom élevé) */}
      {zoom >= 2.0 && !isUnexplored && (
        <g className="planet-details">
          {/* Température */}
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

          {/* Population pour planètes possédées */}
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

      {/* Point rouge clignotant pour nova imminente */}
      {planet.nova_turn && !planet.is_nova && (
        <circle
          cx={planet.x + planetRadius + 2}
          cy={planet.y - planetRadius - 2}
          r={2}
          fill="#ff0000"
          className="danger-blink"
        />
      )}
    </g>
  );
}

export default PlanetMarker;
