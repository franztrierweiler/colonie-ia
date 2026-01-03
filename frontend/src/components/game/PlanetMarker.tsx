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

      {/* Bicorne 3D Isométrique pour planètes possédées */}
      {isOwned && !isUnexplored && (
        <g transform={`translate(${planet.x}, ${planet.y - planetRadius * 0.9})`}>
          {/* Définitions des dégradés pour effet 3D LEGO */}
          <defs>
            {/* Dégradé face supérieure (lumière du haut) */}
            <linearGradient id={`top-grad-${planet.id}`} x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#3a3a3a" />
              <stop offset="100%" stopColor="#252525" />
            </linearGradient>
            {/* Dégradé face avant (plus sombre) */}
            <linearGradient id={`front-grad-${planet.id}`} x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#1a1a1a" />
              <stop offset="100%" stopColor="#0a0a0a" />
            </linearGradient>
            {/* Dégradé doré */}
            <linearGradient id={`gold-grad-${planet.id}`} x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#ffd700" />
              <stop offset="50%" stopColor="#daa520" />
              <stop offset="100%" stopColor="#996515" />
            </linearGradient>
            {/* Dégradé bleu 3D */}
            <linearGradient id={`blue-grad-${planet.id}`} x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#4488cc" />
              <stop offset="50%" stopColor="#0055a4" />
              <stop offset="100%" stopColor="#003366" />
            </linearGradient>
            {/* Dégradé rouge 3D */}
            <linearGradient id={`red-grad-${planet.id}`} x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#ff6655" />
              <stop offset="50%" stopColor="#ef4135" />
              <stop offset="100%" stopColor="#aa2020" />
            </linearGradient>
            {/* Dégradé ennemi */}
            <linearGradient id={`enemy-top-${planet.id}`} x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor={ownerColor} />
              <stop offset="100%" stopColor={ownerColor} stopOpacity="0.7" />
            </linearGradient>
            <linearGradient id={`enemy-front-${planet.id}`} x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor={ownerColor} stopOpacity="0.5" />
              <stop offset="100%" stopColor="#0a0a0a" />
            </linearGradient>
          </defs>

          {/* Ombre portée du bicorne sur la planète */}
          <ellipse
            cx="0"
            cy={planetRadius * 0.35}
            rx="6"
            ry="2"
            fill="rgba(0,0,0,0.5)"
          />

          {isMine ? (
            /* === BICORNE NAPOLÉONIEN 3D ISOMÉTRIQUE === */
            <g transform="translate(-7, -8) scale(1.5)">

              {/* === POINTE GAUCHE (BLEUE) - Vue 3D === */}
              {/* Face supérieure de la pointe gauche */}
              <path
                d="M0.5,5.5 L2.8,1.2 L3.5,1.8 L1.5,5.2 Z"
                fill={`url(#blue-grad-${planet.id})`}
              />
              {/* Face avant de la pointe gauche (plus sombre) */}
              <path
                d="M0.5,5.5 L1.5,5.2 L1.5,6.2 L0.5,6.5 Z"
                fill="#002244"
              />
              {/* Épaisseur/tranche de la pointe gauche */}
              <path
                d="M0.5,5.5 L0.5,6.5 L0.2,6.3 L0.2,5.3 Z"
                fill="#001133"
              />
              {/* Liseré doré pointe gauche */}
              <path
                d="M0.5,5.5 L2.8,1.2"
                fill="none"
                stroke="#daa520"
                strokeWidth="0.3"
              />
              {/* Reflet sur pointe bleue */}
              <path
                d="M1.8,3 L2.5,1.8 L2.8,2.1 L2.1,3.3 Z"
                fill="#6699dd"
                opacity="0.5"
              />

              {/* === CORPS CENTRAL DU BICORNE === */}
              {/* Face supérieure du corps (vue de dessus légèrement) */}
              <path
                d="M1.5,5.2 L3.5,1.8 L4.5,1.5 L5.5,1.8 L7.5,5.2 L4.5,4.5 Z"
                fill={`url(#top-grad-${planet.id})`}
              />
              {/* Face avant du corps (épaisseur 3D) */}
              <path
                d="M1.5,5.2 L1.5,6.2 L4.5,5.5 L7.5,6.2 L7.5,5.2 L4.5,4.5 Z"
                fill={`url(#front-grad-${planet.id})`}
              />
              {/* Bordure dorée inférieure 3D */}
              <path
                d="M1.5,6.2 L4.5,5.5 L7.5,6.2 L4.5,5.8 Z"
                fill={`url(#gold-grad-${planet.id})`}
              />
              {/* Ligne de séparation (rebord du chapeau) */}
              <path
                d="M1.5,5.2 L4.5,4.5 L7.5,5.2"
                fill="none"
                stroke="#4a4a4a"
                strokeWidth="0.2"
              />

              {/* === POINTE DROITE (ROUGE) - Vue 3D === */}
              {/* Face supérieure de la pointe droite */}
              <path
                d="M8.5,5.5 L6.2,1.2 L5.5,1.8 L7.5,5.2 Z"
                fill={`url(#red-grad-${planet.id})`}
              />
              {/* Face avant de la pointe droite (plus sombre) */}
              <path
                d="M8.5,5.5 L7.5,5.2 L7.5,6.2 L8.5,6.5 Z"
                fill="#661515"
              />
              {/* Épaisseur/tranche de la pointe droite */}
              <path
                d="M8.5,5.5 L8.5,6.5 L8.8,6.3 L8.8,5.3 Z"
                fill="#441010"
              />
              {/* Liseré doré pointe droite */}
              <path
                d="M8.5,5.5 L6.2,1.2"
                fill="none"
                stroke="#daa520"
                strokeWidth="0.3"
              />
              {/* Reflet sur pointe rouge */}
              <path
                d="M7.2,3 L6.5,1.8 L6.2,2.1 L6.9,3.3 Z"
                fill="#ff8866"
                opacity="0.5"
              />

              {/* === COCARDE TRICOLORE 3D === */}
              {/* Ombre portée de la cocarde */}
              <ellipse cx="4.7" cy="3.5" rx="1.2" ry="0.8" fill="rgba(0,0,0,0.4)" />

              {/* Base en relief (cylindre) */}
              <ellipse cx="4.5" cy="3.2" rx="1.1" ry="0.7" fill="#0a0a0a" />
              <ellipse cx="4.5" cy="3" rx="1.1" ry="0.7" fill="#1a1a1a" />

              {/* Anneau bleu extérieur */}
              <ellipse cx="4.5" cy="2.85" rx="1.0" ry="0.65" fill="#002244" />
              <ellipse cx="4.5" cy="2.8" rx="0.95" ry="0.6" fill="#0055a4" />

              {/* Anneau blanc */}
              <ellipse cx="4.5" cy="2.75" rx="0.65" ry="0.4" fill="#cccccc" />
              <ellipse cx="4.5" cy="2.7" rx="0.6" ry="0.38" fill="#ffffff" />

              {/* Centre rouge */}
              <ellipse cx="4.5" cy="2.68" rx="0.35" ry="0.22" fill="#aa2020" />
              <ellipse cx="4.5" cy="2.65" rx="0.3" ry="0.2" fill="#ef4135" />

              {/* Bouton doré central en 3D */}
              <ellipse cx="4.5" cy="2.62" rx="0.15" ry="0.1" fill="#996515" />
              <ellipse cx="4.5" cy="2.6" rx="0.12" ry="0.08" fill="#ffd700" />
              <ellipse cx="4.45" cy="2.58" rx="0.04" ry="0.03" fill="#fff8dc" />

              {/* Reflet global sur le bicorne */}
              <path
                d="M2,4.5 Q3,2.5 4,2 L4.5,2.2 Q3.5,3 2.5,4.8 Z"
                fill="rgba(255,255,255,0.15)"
              />
            </g>
          ) : (
            /* === BICORNE ENNEMI 3D ISOMÉTRIQUE === */
            <g transform="translate(-7, -8) scale(1.5)">

              {/* Pointe gauche */}
              <path
                d="M0.5,5.5 L2.8,1.2 L3.5,1.8 L1.5,5.2 Z"
                fill={`url(#enemy-top-${planet.id})`}
              />
              <path
                d="M0.5,5.5 L1.5,5.2 L1.5,6.2 L0.5,6.5 Z"
                fill="rgba(0,0,0,0.5)"
              />
              <path
                d="M0.5,5.5 L0.5,6.5 L0.2,6.3 L0.2,5.3 Z"
                fill="rgba(0,0,0,0.7)"
              />

              {/* Corps central */}
              <path
                d="M1.5,5.2 L3.5,1.8 L4.5,1.5 L5.5,1.8 L7.5,5.2 L4.5,4.5 Z"
                fill={`url(#enemy-top-${planet.id})`}
              />
              <path
                d="M1.5,5.2 L1.5,6.2 L4.5,5.5 L7.5,6.2 L7.5,5.2 L4.5,4.5 Z"
                fill={`url(#enemy-front-${planet.id})`}
              />
              <path
                d="M1.5,6.2 L4.5,5.5 L7.5,6.2 L4.5,5.8 Z"
                fill="#222"
              />

              {/* Pointe droite */}
              <path
                d="M8.5,5.5 L6.2,1.2 L5.5,1.8 L7.5,5.2 Z"
                fill={`url(#enemy-top-${planet.id})`}
              />
              <path
                d="M8.5,5.5 L7.5,5.2 L7.5,6.2 L8.5,6.5 Z"
                fill="rgba(0,0,0,0.5)"
              />
              <path
                d="M8.5,5.5 L8.5,6.5 L8.8,6.3 L8.8,5.3 Z"
                fill="rgba(0,0,0,0.7)"
              />

              {/* Insigne ennemi 3D */}
              <ellipse cx="4.7" cy="3.5" rx="1.0" ry="0.7" fill="rgba(0,0,0,0.4)" />
              <ellipse cx="4.5" cy="3.1" rx="0.9" ry="0.6" fill="#0a0a0a" />
              <ellipse cx="4.5" cy="2.9" rx="0.85" ry="0.55" fill="#1a1a1a" />
              <ellipse cx="4.5" cy="2.75" rx="0.6" ry="0.4" fill="#2a2a2a" />
              <ellipse cx="4.5" cy="2.65" rx="0.35" ry="0.25" fill="#3a3a3a" />
              <ellipse cx="4.45" cy="2.6" rx="0.1" ry="0.07" fill="#555" />

              {/* Contours */}
              <path d="M0.5,5.5 L2.8,1.2" fill="none" stroke="#333" strokeWidth="0.2" />
              <path d="M8.5,5.5 L6.2,1.2" fill="none" stroke="#333" strokeWidth="0.2" />
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
