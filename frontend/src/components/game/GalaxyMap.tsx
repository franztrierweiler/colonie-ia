import { useRef, useState, useCallback, useMemo } from 'react';
import type { Planet, Fleet, Player } from '../../hooks/useGameState';
import PlanetMarker from './PlanetMarker';
import FleetTrajectory from './FleetTrajectory';
import ShipSelectionModal from './ShipSelectionModal';
import './GalaxyMap.css';

interface GalaxyMapProps {
  width: number;
  height: number;
  planets: Planet[];
  fleets: Fleet[];
  players: Player[];
  myPlayerId: number;
  currentTurn?: number;
  selectedPlanetId: number | null;
  selectedFleetId: number | null;
  onPlanetClick: (planetId: number) => void;
  onFleetClick: (fleetId: number) => void;
  onMoveFleet?: (fleetId: number, destinationPlanetId: number) => void;
  onSendShips?: (originPlanetId: number, destinationPlanetId: number, shipsToSend: Record<string, number>) => void;
}

// État pour le flux d'envoi de vaisseaux
interface ShipSendState {
  originPlanetId: number | null;
  selectedShips: Record<string, number>;
  isModalOpen: boolean;
}

// Niveaux de zoom prédéfinis
const ZOOM_LEVELS = {
  galaxy: 0.5,
  region: 1.0,
  system: 2.0,
};

const MIN_ZOOM = 0.25;
const MAX_ZOOM = 4.0;
const ZOOM_SENSITIVITY = 0.001;

function GalaxyMap({
  width,
  height,
  planets,
  fleets,
  players,
  myPlayerId,
  currentTurn = 1,
  selectedPlanetId,
  selectedFleetId,
  onPlanetClick,
  onFleetClick,
  onMoveFleet,
  onSendShips,
}: GalaxyMapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [hasMoved, setHasMoved] = useState(false);

  // État pour le drag de flotte (ref pour accès synchrone dans les callbacks)
  const [draggingFleetId, setDraggingFleetId] = useState<number | null>(null);
  const draggingFleetIdRef = useRef<number | null>(null);
  const [dragLine, setDragLine] = useState<{ fromX: number; fromY: number; toX: number; toY: number } | null>(null);
  const dragLineRef = useRef<{ fromX: number; fromY: number; toX: number; toY: number } | null>(null);
  const [hoveredPlanetId, setHoveredPlanetId] = useState<number | null>(null);

  // État pour le flux d'envoi de vaisseaux (nouveau système)
  const [shipSendState, setShipSendState] = useState<ShipSendState>({
    originPlanetId: null,
    selectedShips: {},
    isModalOpen: false,
  });

  const getPlayerColor = useCallback(
    (playerId: number | null): string => {
      if (!playerId) return '#666';
      const player = players.find((p) => p.id === playerId);
      return player?.color || '#666';
    },
    [players]
  );

  // Calculer les vaisseaux stationnés par planète (agrégé de toutes les flottes)
  const stationedShipsByPlanet = useMemo(() => {
    const result: Record<number, { total: number; byType: Record<string, number> }> = {};

    for (const fleet of fleets) {
      if (fleet.status === 'stationed' && fleet.current_planet_id && fleet.player_id === myPlayerId) {
        if (!result[fleet.current_planet_id]) {
          result[fleet.current_planet_id] = { total: 0, byType: {} };
        }
        result[fleet.current_planet_id].total += fleet.ship_count;

        // Agréger par type
        for (const [type, count] of Object.entries(fleet.ships_by_type)) {
          result[fleet.current_planet_id].byType[type] =
            (result[fleet.current_planet_id].byType[type] || 0) + count;
        }
      }
    }

    return result;
  }, [fleets, myPlayerId]);

  // Calculer les indicateurs orbitaux par planète
  const orbitalIndicators = useMemo(() => {
    const result: Record<number, { hasSatellite: boolean; hasConstruction: boolean }> = {};

    for (const fleet of fleets) {
      if (fleet.status === 'stationed' && fleet.current_planet_id) {
        if (!result[fleet.current_planet_id]) {
          result[fleet.current_planet_id] = { hasSatellite: false, hasConstruction: false };
        }

        // Vérifier les satellites
        const satelliteCount = fleet.ships_by_type['satellite'] || 0;
        if (satelliteCount > 0) {
          result[fleet.current_planet_id].hasSatellite = true;
        }
      }
    }

    // Vérifier les constructions en cours (planètes avec budget ships > 33% par défaut)
    for (const planet of planets) {
      if (planet.owner_id === myPlayerId && (planet.ships_budget || 0) > 33) {
        if (!result[planet.id]) {
          result[planet.id] = { hasSatellite: false, hasConstruction: false };
        }
        result[planet.id].hasConstruction = true;
      }
    }

    return result;
  }, [fleets, planets, myPlayerId]);

  // Handlers pour le flux d'envoi de vaisseaux
  const handleShipBadgeClick = useCallback((planetId: number) => {
    setShipSendState({
      originPlanetId: planetId,
      selectedShips: {},
      isModalOpen: true,
    });
  }, []);

  const handleShipSelectionComplete = useCallback((selection: Record<string, number>) => {
    // TODO: Implémenter le nouveau système d'envoi de vaisseaux
    setShipSendState({
      originPlanetId: null,
      selectedShips: {},
      isModalOpen: false,
    });
  }, []);

  const handleShipSelectionClose = useCallback(() => {
    setShipSendState({
      originPlanetId: null,
      selectedShips: {},
      isModalOpen: false,
    });
  }, []);

  // Gestion du zoom avec la molette
  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    const delta = -e.deltaY * ZOOM_SENSITIVITY;
    setZoom((z) => Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, z * (1 + delta))));
  }, []);

  // Zoom prédéfinis
  const handleZoomLevel = useCallback((level: keyof typeof ZOOM_LEVELS) => {
    setZoom(ZOOM_LEVELS[level]);
    if (level === 'galaxy') {
      setPan({ x: 0, y: 0 });
    }
  }, []);

  const handleZoomIn = useCallback(() => {
    setZoom((z) => Math.min(MAX_ZOOM, z * 1.5));
  }, []);

  const handleZoomOut = useCallback(() => {
    setZoom((z) => Math.max(MIN_ZOOM, z / 1.5));
  }, []);

  const handleZoomReset = useCallback(() => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  }, []);

  // Gestion du drag de flotte (déclarés avant handleMouseMove qui les utilise)
  const handleFleetDragStart = useCallback((fleetId: number, startX: number, startY: number) => {
    const fleet = fleets.find(f => f.id === fleetId);
    if (!fleet || fleet.player_id !== myPlayerId || fleet.status !== 'stationed') return;

    const line = { fromX: startX, fromY: startY, toX: startX, toY: startY };
    draggingFleetIdRef.current = fleetId;
    dragLineRef.current = line;
    setDraggingFleetId(fleetId);
    setDragLine(line);
  }, [fleets, myPlayerId]);

  const handleFleetDragMove = useCallback((e: React.MouseEvent) => {
    // Utiliser les refs pour accès synchrone
    if (!draggingFleetIdRef.current || !containerRef.current || !dragLineRef.current) return;

    const container = containerRef.current;
    const rect = container.getBoundingClientRect();

    // Convertir les coordonnées écran en coordonnées SVG
    const svgX = (e.clientX - rect.left - pan.x) / zoom;
    const svgY = (e.clientY - rect.top - pan.y) / zoom;

    const newLine = { ...dragLineRef.current, toX: svgX, toY: svgY };
    dragLineRef.current = newLine;
    setDragLine(newLine);

    // Vérifier si on survole une planète
    const hovered = planets.find(p => {
      const pdx = p.x - svgX;
      const pdy = p.y - svgY;
      return Math.sqrt(pdx * pdx + pdy * pdy) < 10; // Rayon de détection
    });
    setHoveredPlanetId(hovered?.id || null);
  }, [pan, zoom, planets]);

  // Démarrer le drag depuis une planète (quand une flotte est sélectionnée)
  const handlePlanetDragStart = useCallback((planetId: number, planetX: number, planetY: number) => {
    // Vérifier si une flotte sélectionnée est sur cette planète
    if (selectedFleetId) {
      const fleet = fleets.find(f => f.id === selectedFleetId);
      if (fleet && fleet.current_planet_id === planetId && fleet.player_id === myPlayerId && fleet.status === 'stationed') {
        const line = { fromX: planetX, fromY: planetY, toX: planetX, toY: planetY };
        draggingFleetIdRef.current = selectedFleetId;
        dragLineRef.current = line;
        setDraggingFleetId(selectedFleetId);
        setDragLine(line);
        return true;
      }
    }
    return false;
  }, [selectedFleetId, fleets, myPlayerId]);

  const handleFleetDragEnd = useCallback(() => {
    const fleetId = draggingFleetIdRef.current;
    if (fleetId && hoveredPlanetId && onMoveFleet) {
      const fleet = fleets.find(f => f.id === fleetId);
      // Ne pas déplacer vers la même planète
      if (fleet && fleet.current_planet_id !== hoveredPlanetId) {
        onMoveFleet(fleetId, hoveredPlanetId);
      }
    }
    draggingFleetIdRef.current = null;
    dragLineRef.current = null;
    setDraggingFleetId(null);
    setDragLine(null);
    setHoveredPlanetId(null);
  }, [hoveredPlanetId, onMoveFleet, fleets]);

  // Gestion du pan avec drag
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (e.button === 0) { // Clic gauche
      setIsDragging(true);
      setHasMoved(false);
      setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    }
  }, [pan]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    // Si on drag une flotte, gérer ça en priorité (utiliser ref pour accès synchrone)
    if (draggingFleetIdRef.current) {
      handleFleetDragMove(e);
      return;
    }

    if (isDragging) {
      const dx = Math.abs(e.clientX - (dragStart.x + pan.x));
      const dy = Math.abs(e.clientY - (dragStart.y + pan.y));
      // Ne commencer le drag que si on a bougé de plus de 3 pixels
      if (dx > 3 || dy > 3) {
        setHasMoved(true);
        setPan({
          x: e.clientX - dragStart.x,
          y: e.clientY - dragStart.y,
        });
      }
    }
  }, [isDragging, dragStart, pan, handleFleetDragMove]);

  const handleMouseUp = useCallback(() => {
    if (draggingFleetIdRef.current) {
      handleFleetDragEnd();
    }
    setIsDragging(false);
  }, [handleFleetDragEnd]);

  const handleMouseLeave = useCallback(() => {
    if (draggingFleetIdRef.current) {
      handleFleetDragEnd();
    }
    setIsDragging(false);
    setHasMoved(false);
  }, [handleFleetDragEnd]);

  // Flottes en transit (pour trajectoires)
  const fleetsInTransit = fleets.filter(
    (f) => f.status === 'in_transit' && f.destination_planet_id
  );

  // Flottes stationnées (pour marqueurs)
  const stationedFleets = fleets.filter(
    (f) => f.status === 'stationed' && f.current_planet_id
  );

  return (
    <div
      ref={containerRef}
      className="galaxy-map-container"
      onWheel={handleWheel}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseLeave}
    >
      {/* Contrôles de zoom */}
      <div className="zoom-controls">
        <button onClick={handleZoomIn} title="Zoom +">+</button>
        <button onClick={handleZoomReset} title="Reset">1:1</button>
        <button onClick={handleZoomOut} title="Zoom -">-</button>
        <div className="zoom-divider" />
        <button
          onClick={() => handleZoomLevel('galaxy')}
          className={zoom <= 0.6 ? 'active' : ''}
          title="Vue galaxie"
        >
          G
        </button>
        <button
          onClick={() => handleZoomLevel('region')}
          className={zoom > 0.6 && zoom <= 1.5 ? 'active' : ''}
          title="Vue région"
        >
          R
        </button>
        <button
          onClick={() => handleZoomLevel('system')}
          className={zoom > 1.5 ? 'active' : ''}
          title="Vue système"
        >
          S
        </button>
      </div>

      {/* Indicateur de zoom */}
      <div className="zoom-indicator">
        {Math.round(zoom * 100)}%
      </div>

      {/* Carte SVG */}
      <svg
        className={`galaxy-map ${isDragging ? 'dragging' : ''}`}
        viewBox={`0 0 ${width} ${height}`}
        style={{
          transform: `scale(${zoom}) translate(${pan.x / zoom}px, ${pan.y / zoom}px)`,
        }}
      >
        {/* Fond étoilé et textures */}
        <defs>
          <radialGradient id="starGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#ffffff" stopOpacity="1" />
            <stop offset="100%" stopColor="#ffffff" stopOpacity="0" />
          </radialGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="1" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          {/* Texture planète inconnue - points de balayage */}
          <pattern id="unknownPattern" patternUnits="userSpaceOnUse" width="2" height="2">
            <rect width="2" height="2" fill="#3a3a4a" />
            <circle cx="1" cy="1" r="0.4" fill="#4a4a5a" />
            <rect x="0" y="0" width="0.5" height="0.5" fill="#2a2a3a" />
          </pattern>

          {/* Texture astéroïde - surface lunaire avec cratères */}
          <pattern id="asteroidPattern" patternUnits="userSpaceOnUse" width="3" height="3">
            <rect width="3" height="3" fill="#888" />
            <circle cx="0.8" cy="0.8" r="0.5" fill="#666" />
            <circle cx="2.2" cy="1.8" r="0.4" fill="#777" />
            <circle cx="1.5" cy="2.5" r="0.3" fill="#6a6a6a" />
          </pattern>

          {/* Texture planète hostile rocheuse - gris foncé avec cratères */}
          <pattern id="hostilePattern" patternUnits="userSpaceOnUse" width="3" height="3">
            <rect width="3" height="3" fill="#444" />
            <circle cx="0.7" cy="0.7" r="0.6" fill="#333" />
            <circle cx="2.3" cy="1.5" r="0.5" fill="#3a3a3a" />
            <circle cx="1.2" cy="2.3" r="0.4" fill="#383838" />
          </pattern>

          {/* Texture planète gazeuse hostile - orange-rouge en mouvement */}
          <pattern id="gaseousPattern" patternUnits="userSpaceOnUse" width="4" height="4">
            <rect width="4" height="4" fill="#884422" />
            <ellipse cx="2" cy="1" rx="1.5" ry="0.4" fill="#aa5533" opacity="0.8" />
            <ellipse cx="2" cy="2.5" rx="1.8" ry="0.5" fill="#cc6644" opacity="0.7" />
            <ellipse cx="1" cy="3.5" rx="1.2" ry="0.3" fill="#995533" opacity="0.6" />
          </pattern>

          {/* Texture planète habitable - aspect Terre (bleu/vert) */}
          <pattern id="habitablePattern" patternUnits="userSpaceOnUse" width="4" height="4">
            <rect width="4" height="4" fill="#2266aa" />
            {/* Continents */}
            <ellipse cx="1" cy="1.5" rx="0.8" ry="1" fill="#338844" />
            <ellipse cx="3" cy="2.5" rx="1" ry="0.7" fill="#448855" />
            <circle cx="2.5" cy="0.8" r="0.5" fill="#44aa66" />
            {/* Nuages */}
            <ellipse cx="0.5" cy="0.5" rx="0.6" ry="0.3" fill="#ffffff" opacity="0.3" />
            <ellipse cx="3" cy="3.5" rx="0.8" ry="0.25" fill="#ffffff" opacity="0.25" />
          </pattern>

          {/* Gradient pour effet 3D sur astéroïde */}
          <radialGradient id="asteroidGradient" cx="30%" cy="30%" r="70%">
            <stop offset="0%" stopColor="#aaa" />
            <stop offset="100%" stopColor="#666" />
          </radialGradient>
        </defs>

        {/* Background */}
        <rect x="0" y="0" width={width} height={height} fill="#0a0a1a" />

        {/* Étoiles de fond (décoratives) */}
        {Array.from({ length: 100 }).map((_, i) => (
          <circle
            key={`bg-star-${i}`}
            cx={Math.random() * width}
            cy={Math.random() * height}
            r={Math.random() * 0.5 + 0.2}
            fill="#ffffff"
            opacity={Math.random() * 0.5 + 0.1}
          />
        ))}

        {/* Trajectoires des flottes */}
        {fleetsInTransit.map((fleet) => {
          const toPlanet = planets.find((p) => p.id === fleet.destination_planet_id);
          if (!toPlanet) return null;

          // Calculer la progression (0-1) basée sur le tour actuel
          let progress = 0.5;
          if (fleet.departure_turn && fleet.arrival_turn) {
            const totalTurns = fleet.arrival_turn - fleet.departure_turn;
            const elapsedTurns = currentTurn - fleet.departure_turn;
            progress = totalTurns > 0 ? Math.min(1, Math.max(0, elapsedTurns / totalTurns)) : 0.5;
          }

          // Estimer la position de départ
          // On utilise un angle basé sur l'ID de flotte pour avoir une direction stable
          const estimatedDistance = fleet.fleet_speed * (fleet.arrival_turn! - fleet.departure_turn!);
          const angle = (fleet.id * 137.5) % 360 * (Math.PI / 180); // Angle stable basé sur l'ID

          // Position de départ estimée (opposée à la destination)
          const fromX = toPlanet.x - estimatedDistance * Math.cos(angle);
          const fromY = toPlanet.y - estimatedDistance * Math.sin(angle);

          return (
            <FleetTrajectory
              key={`trajectory-${fleet.id}`}
              fromX={fromX}
              fromY={fromY}
              toX={toPlanet.x}
              toY={toPlanet.y}
              color={getPlayerColor(fleet.player_id)}
              isMine={fleet.player_id === myPlayerId}
              progress={progress}
              arrivalTurn={fleet.arrival_turn || undefined}
              fleetName={fleet.name}
              shipCount={fleet.ship_count}
            />
          );
        })}

        {/* Planètes */}
        {planets.map((planet) => {
          // Vérifier si cette planète a une flotte sélectionnée qu'on peut draguer
          const selectedFleet = selectedFleetId ? fleets.find(f => f.id === selectedFleetId) : null;
          const canDragFromPlanet = selectedFleet
            && selectedFleet.current_planet_id === planet.id
            && selectedFleet.player_id === myPlayerId
            && selectedFleet.status === 'stationed';

          const orbital = orbitalIndicators[planet.id];

          return (
            <PlanetMarker
              key={planet.id}
              planet={planet}
              isSelected={planet.id === selectedPlanetId}
              myPlayerId={myPlayerId}
              zoom={zoom}
              getPlayerColor={getPlayerColor}
              onClick={() => onPlanetClick(planet.id)}
              canDrag={canDragFromPlanet}
              onDragStart={() => handlePlanetDragStart(planet.id, planet.x, planet.y)}
              stationedShipCount={stationedShipsByPlanet[planet.id]?.total || 0}
              onShipBadgeClick={() => handleShipBadgeClick(planet.id)}
              hasSatellite={orbital?.hasSatellite || false}
              hasShipsInConstruction={orbital?.hasConstruction || false}
            />
          );
        })}

        {/* Note: FleetMarker supprimé - les vaisseaux sont affichés via ShipCountBadge */}

        {/* Ligne de drag de flotte avec distance */}
        {dragLine && (() => {
          const dx = dragLine.toX - dragLine.fromX;
          const dy = dragLine.toY - dragLine.fromY;
          const distance = Math.sqrt(dx * dx + dy * dy);
          return (
            <g className="fleet-drag-line">
              <line
                x1={dragLine.fromX}
                y1={dragLine.fromY}
                x2={dragLine.toX}
                y2={dragLine.toY}
                stroke={hoveredPlanetId ? '#4ade80' : '#ffa500'}
                strokeWidth="1.5"
                strokeDasharray="4 2"
                opacity="0.9"
              />
              {/* Cercle à la destination */}
              <circle
                cx={dragLine.toX}
                cy={dragLine.toY}
                r="4"
                fill={hoveredPlanetId ? '#4ade80' : '#ffa500'}
                opacity="0.7"
              />
              {/* Affichage de la distance */}
              {distance > 5 && (
                <g>
                  {/* Fond pour le texte */}
                  <rect
                    x={(dragLine.fromX + dragLine.toX) / 2 - 15}
                    y={(dragLine.fromY + dragLine.toY) / 2 - 8}
                    width="30"
                    height="12"
                    fill="#000"
                    opacity="0.7"
                    rx="2"
                  />
                  {/* Texte de distance */}
                  <text
                    x={(dragLine.fromX + dragLine.toX) / 2}
                    y={(dragLine.fromY + dragLine.toY) / 2 + 1}
                    fill={hoveredPlanetId ? '#4ade80' : '#ffa500'}
                    fontSize="8"
                    fontWeight="bold"
                    textAnchor="middle"
                    dominantBaseline="middle"
                  >
                    {distance.toFixed(1)}
                  </text>
                </g>
              )}
            </g>
          );
        })()}

      </svg>

      {/* Modale de sélection de vaisseaux (en dehors du SVG) */}
      {shipSendState.isModalOpen && shipSendState.originPlanetId && (
        <ShipSelectionModal
          isOpen={shipSendState.isModalOpen}
          onClose={handleShipSelectionClose}
          availableShips={stationedShipsByPlanet[shipSendState.originPlanetId]?.byType || {}}
          planetName={planets.find(p => p.id === shipSendState.originPlanetId)?.name || ''}
          onSelectionComplete={handleShipSelectionComplete}
        />
      )}
    </div>
  );
}

export default GalaxyMap;
