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

  // Détection planète gazeuse : gravité quasi-nulle (< 0.2g)
  const isGaseous = planet.gravity < 0.2;

  // Détection planète hostile : température extrême OU gravité extrême
  const isHostile = !isUnexplored && (
    planet.current_temperature < -50 ||
    planet.current_temperature > 80 ||
    planet.gravity > 3.0 ||
    planet.gravity < 0.1
  );

  // Détection astéroïde/minerai : faible habitabilité et présence de métal
  const isAsteroid = !isUnexplored && !isHostile && planet.habitability < 0.2 && planet.metal_reserves > 0;

  // Niveau de terraformation basé sur l'habitabilité (0 à 1)
  // L'habitabilité combine température et gravité
  const terraformLevel = isUnexplored ? 0 : planet.habitability;

  // Potentiel max de terraformation basé uniquement sur la gravité
  // (la température peut être modifiée, pas la gravité)
  const getMaxTerraformPotential = () => {
    const gravityDiff = Math.abs(planet.gravity - 1.0);
    return Math.max(0, 1 - gravityDiff / 2);
  };
  const maxTerraformPotential = getMaxTerraformPotential();

  // Taille selon sélection (plus grand pour voir les textures)
  const planetRadius = isSelected ? 6 : 5;
  const glowRadius = isSelected ? 8 : 7;

  // Couleur ou texture de la planète selon UI_SPECS.md
  const getPlanetFill = () => {
    // Planète inexplorée = texture mystérieuse gris foncé
    if (isUnexplored) return 'url(#unknownPattern)';

    // Planète hostile gazeuse = orange-rouge
    if (isHostile && isGaseous) return 'url(#gaseousPattern)';

    // Planète hostile rocheuse = gris foncé avec points de lave
    if (isHostile) return 'url(#hostilePattern)';

    // Astéroïde/minerai = texture rocheuse lunaire
    if (isAsteroid) return 'url(#asteroidPattern)';

    // Planète bien terraformée (>85%) = bleu intense avec aspect Terre
    if (terraformLevel > 0.85) {
      return 'url(#habitablePattern)';
    }

    // Planètes terraformables : gradient de gris clair vers bleu
    // Basé sur le pourcentage de terraformation actuel
    // Gris clair (180, 180, 190) vers bleu (70, 130, 200)
    const r = Math.floor(180 - terraformLevel * 110);
    const g = Math.floor(180 - terraformLevel * 50);
    const b = Math.floor(190 + terraformLevel * 10);
    return `rgb(${r}, ${g}, ${b})`;
  };

  // Génère des cratères selon le potentiel de terraformation
  // < 20% potentiel = cratères très prononcés (beaucoup de métal)
  // < 50% potentiel = quelques cratères (un peu de métal)
  // > 50% potentiel = pas de cratères visibles
  const renderCraters = () => {
    // Pas de cratères pour les planètes inexplorées, hostiles ou bien terraformables
    if (isUnexplored || isHostile || maxTerraformPotential > 0.5) return null;
    // Pas de cratères pour les planètes déjà bien terraformées
    if (terraformLevel > 0.5) return null;

    const craters = [];
    const seed = planet.id;

    // Nombre et taille des cratères selon le potentiel
    const craterCount = maxTerraformPotential < 0.2 ? 6 : 3;
    const craterSizeMultiplier = maxTerraformPotential < 0.2 ? 1.5 : 1.0;

    for (let i = 0; i < craterCount; i++) {
      const angle = ((seed * (i + 1) * 137) % 360) * (Math.PI / 180);
      const distance = 0.3 + ((seed * (i + 2)) % 50) / 100;
      const cx = planet.x + Math.cos(angle) * planetRadius * distance;
      const cy = planet.y + Math.sin(angle) * planetRadius * distance;
      const r = (0.3 + ((seed * (i + 3)) % 30) / 100) * craterSizeMultiplier;
      craters.push(
        <circle
          key={`crater-${i}`}
          cx={cx}
          cy={cy}
          r={r}
          fill="#555"
          opacity="0.7"
        />
      );
    }
    return craters;
  };

  // Génère des points de lave pour les planètes hostiles rocheuses
  const renderLavaPoints = () => {
    if (!isHostile || isGaseous) return null;

    const lavaPoints = [];
    const seed = planet.id;

    for (let i = 0; i < 5; i++) {
      const angle = ((seed * (i + 1) * 97) % 360) * (Math.PI / 180);
      const distance = 0.2 + ((seed * (i + 2)) % 40) / 100;
      const cx = planet.x + Math.cos(angle) * planetRadius * distance;
      const cy = planet.y + Math.sin(angle) * planetRadius * distance;
      lavaPoints.push(
        <circle
          key={`lava-${i}`}
          cx={cx}
          cy={cy}
          r={0.4}
          fill="#ff4422"
          opacity="0.8"
        />
      );
    }
    return lavaPoints;
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
          fill={planet.is_nova ? '#ff4444' : getPlanetFill()}
          opacity="0.2"
          filter="url(#glow)"
        />
      )}

      {/* Coeur de la planète */}
      <circle
        cx={planet.x}
        cy={planet.y}
        r={planetRadius}
        fill={planet.is_nova ? '#ff0000' : getPlanetFill()}
        className="planet-core"
      />

      {/* Effet d'auto-rotation (ombre qui traverse la surface) */}
      {!isUnexplored && !planet.is_nova && (
        <g clipPath={`url(#planet-clip-${planet.id})`}>
          <defs>
            <clipPath id={`planet-clip-${planet.id}`}>
              <circle cx={planet.x} cy={planet.y} r={planetRadius - 0.5} />
            </clipPath>
          </defs>
          <ellipse
            cx={planet.x}
            cy={planet.y}
            rx={planetRadius * 0.4}
            ry={planetRadius * 1.2}
            fill="rgba(0,0,0,0.2)"
            className="planet-terminator"
            style={{
              ['--planet-x' as string]: `${planet.x}px`,
              ['--planet-radius' as string]: `${planetRadius}px`,
            }}
          />
        </g>
      )}

      {/* Cratères pour planètes à faible potentiel */}
      {renderCraters()}

      {/* Points de lave pour planètes hostiles rocheuses */}
      {renderLavaPoints()}

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

      {/* Panneau danger triangulaire pour nova imminente */}
      {planet.nova_turn && !planet.is_nova && (
        <g transform={`translate(${planet.x + planetRadius + 2}, ${planet.y - planetRadius - 2})`}>
          {/* Triangle d'avertissement */}
          <path
            d="M6,0 L12,10 L0,10 Z"
            fill="#ffcc00"
            stroke="#222"
            strokeWidth="0.5"
          />
          {/* Bordure intérieure */}
          <path
            d="M6,1.5 L10.5,9 L1.5,9 Z"
            fill="none"
            stroke="#222"
            strokeWidth="0.3"
          />
          {/* Point d'exclamation */}
          <rect x="5" y="3.5" width="2" height="3.5" fill="#222" />
          <circle cx="6" cy="8" r="1" fill="#222" />
        </g>
      )}
    </g>
  );
}

export default PlanetMarker;
