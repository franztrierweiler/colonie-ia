import { useRef, useState, useCallback, useEffect } from 'react';
import type { Star, Fleet, Player } from '../../hooks/useGameState';
import StarSystem from './StarSystem';
import FleetMarker from './FleetMarker';
import FleetTrajectory from './FleetTrajectory';
import './GalaxyMap.css';

interface GalaxyMapProps {
  width: number;
  height: number;
  stars: Star[];
  fleets: Fleet[];
  players: Player[];
  myPlayerId: number;
  selectedStarId: number | null;
  onStarClick: (starId: number) => void;
  onFleetClick: (fleetId: number) => void;
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
  stars,
  fleets,
  players,
  myPlayerId,
  selectedStarId,
  onStarClick,
  onFleetClick,
}: GalaxyMapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  const getPlayerColor = useCallback(
    (playerId: number | null): string => {
      if (!playerId) return '#666';
      const player = players.find((p) => p.id === playerId);
      return player?.color || '#666';
    },
    [players]
  );

  // Gestion du zoom avec la molette
  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    const delta = -e.deltaY * ZOOM_SENSITIVITY;
    setZoom((z) => Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, z * (1 + delta))));
  }, []);

  // Gestion du pan avec drag
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (e.button === 0) { // Clic gauche
      setIsDragging(true);
      setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    }
  }, [pan]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (isDragging) {
      setPan({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
      });
    }
  }, [isDragging, dragStart]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleMouseLeave = useCallback(() => {
    setIsDragging(false);
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

  // Centrer sur une étoile sélectionnée
  useEffect(() => {
    if (selectedStarId && containerRef.current) {
      const star = stars.find((s) => s.id === selectedStarId);
      if (star) {
        const container = containerRef.current;
        const containerWidth = container.clientWidth;
        const containerHeight = container.clientHeight;

        // Centrer la vue sur l'étoile
        const targetX = containerWidth / 2 - star.x * zoom;
        const targetY = containerHeight / 2 - star.y * zoom;
        setPan({ x: targetX, y: targetY });
      }
    }
  }, [selectedStarId, stars, zoom]);

  // Flottes en transit (pour trajectoires)
  const fleetsInTransit = fleets.filter(
    (f) => f.status === 'in_transit' && f.current_star_id && f.destination_star_id
  );

  // Flottes stationnées (pour marqueurs)
  const stationedFleets = fleets.filter(
    (f) => f.status === 'stationed' && f.current_star_id
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
        {/* Fond étoilé */}
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
          const fromStar = stars.find((s) => s.id === fleet.current_star_id);
          const toStar = stars.find((s) => s.id === fleet.destination_star_id);
          if (!fromStar || !toStar) return null;
          return (
            <FleetTrajectory
              key={`trajectory-${fleet.id}`}
              fromX={fromStar.x}
              fromY={fromStar.y}
              toX={toStar.x}
              toY={toStar.y}
              color={getPlayerColor(fleet.player_id)}
              isMine={fleet.player_id === myPlayerId}
            />
          );
        })}

        {/* Systèmes stellaires */}
        {stars.map((star) => (
          <StarSystem
            key={star.id}
            star={star}
            isSelected={star.id === selectedStarId}
            myPlayerId={myPlayerId}
            zoom={zoom}
            getPlayerColor={getPlayerColor}
            onClick={() => onStarClick(star.id)}
          />
        ))}

        {/* Marqueurs de flottes */}
        {stationedFleets.map((fleet) => {
          const star = stars.find((s) => s.id === fleet.current_star_id);
          if (!star) return null;
          return (
            <FleetMarker
              key={`fleet-${fleet.id}`}
              fleet={fleet}
              x={star.x}
              y={star.y}
              color={getPlayerColor(fleet.player_id)}
              isMine={fleet.player_id === myPlayerId}
              zoom={zoom}
              onClick={() => onFleetClick(fleet.id)}
            />
          );
        })}
      </svg>
    </div>
  );
}

export default GalaxyMap;
