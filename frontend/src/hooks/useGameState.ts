import { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

// Types
export interface Planet {
  id: number;
  name: string;
  galaxy_id: number;
  x: number;
  y: number;
  is_nova: boolean;
  nova_turn: number | null;
  temperature: number;
  current_temperature: number;
  gravity: number;
  metal_reserves: number;
  metal_remaining: number;
  state: string;
  owner_id: number | null;
  population: number;
  max_population: number;
  habitability: number;
  terraform_budget: number;
  mining_budget: number;
  ships_budget: number;
  ship_production_points: number;
  is_home_planet: boolean;
  history_line1: string | null;
  history_line2: string | null;
  texture_type: string | null;
  texture_index: number | null;
}

export interface ProductionQueueItem {
  id: number;
  planet_id: number;
  design_id: number;
  design_name: string | null;
  ship_type: string | null;
  fleet_id: number | null;
  priority: number;
  production_invested: number;
  production_required: number;
  production_progress: number;
  is_completed: boolean;
  is_ready: boolean;
}

export interface Fleet {
  id: number;
  name: string;
  player_id: number;
  status: string;
  current_planet_id: number | null;
  destination_planet_id: number | null;
  departure_turn: number | null;
  arrival_turn: number | null;
  ship_count: number;
  fleet_speed: number;
  fleet_range: number;
  fuel_remaining: number;
  max_fuel: number;
  total_weapons: number;
  total_shields: number;
  combat_behavior: string;
  can_colonize: boolean;
  ships_by_type: Record<string, number>;
}

export interface ShipDesign {
  id: number;
  player_id: number;
  name: string;
  ship_type: string;
  range_level: number;
  speed_level: number;
  weapons_level: number;
  shields_level: number;
  mini_level: number;
  effective_range: number;
  effective_speed: number;
  effective_weapons: number;
  effective_shields: number;
  prototype_cost_money: number;
  prototype_cost_metal: number;
  production_cost_money: number;
  production_cost_metal: number;
  is_prototype_built: boolean;
  ships_built: number;
}

export interface Ship {
  id: number;
  design_id: number;
  design_name: string;
  ship_type: string;
  fleet_id: number | null;
  damage: number;
  health_percent: number;
  is_destroyed: boolean;
}

export const SHIP_TYPES = {
  fighter: { name: 'Chasseur', icon: '⚔️' },
  scout: { name: 'Éclaireur', icon: '🔭' },
  colony: { name: 'Vaisseau Colonial', icon: '🏠' },
  satellite: { name: 'Satellite', icon: '🛰️' },
  tanker: { name: 'Ravitailleur', icon: '⛽' },
  battleship: { name: 'Cuirassé', icon: '🚀' },
  decoy: { name: 'Leurre', icon: '🎭' },
  biological: { name: 'Biologique', icon: '🦠' },
} as const;

export interface Player {
  id: number;
  player_name: string;
  color: string;
  is_ai: boolean;
  money: number;
  metal: number;
}

export interface Galaxy {
  id: number;
  width: number;
  height: number;
  shape: string;
  planet_count: number;
}

export interface GameState {
  gameId: number;
  turn: number;
  myPlayerId: number;
  galaxy: Galaxy;
  planets: Planet[];
  fleets: Fleet[];
  players: Player[];
}

interface UseGameStateReturn {
  gameState: GameState | null;
  isLoading: boolean;
  error: string | null;
  selectedPlanetId: number | null;
  selectedFleetId: number | null;
  setSelectedPlanetId: (id: number | null) => void;
  setSelectedFleetId: (id: number | null) => void;
  refreshMap: () => Promise<void>;
  getPlayerColor: (playerId: number | null) => string;
  getPlanetById: (planetId: number) => Planet | undefined;
  getFleetById: (fleetId: number) => Fleet | undefined;
  getFleetsAtPlanet: (planetId: number) => Fleet[];
  getMyFleets: () => Fleet[];
}

export function useGameState(gameId: number | undefined): UseGameStateReturn {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPlanetId, setSelectedPlanetId] = useState<number | null>(null);
  const [selectedFleetId, setSelectedFleetId] = useState<number | null>(null);

  const refreshMap = useCallback(async () => {
    if (!gameId) return;

    try {
      setIsLoading(true);
      const data = await api.getGameMap(gameId);

      setGameState({
        gameId: data.game_id,
        turn: data.turn,
        myPlayerId: data.my_player_id,
        galaxy: data.galaxy,
        planets: data.planets,
        fleets: data.fleets,
        players: data.players,
      });
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erreur de chargement';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [gameId]);

  useEffect(() => {
    refreshMap();
  }, [refreshMap]);

  const getPlayerColor = useCallback(
    (playerId: number | null): string => {
      if (!playerId || !gameState) return '#666';
      const player = gameState.players.find((p) => p.id === playerId);
      return player?.color || '#666';
    },
    [gameState]
  );

  const getPlanetById = useCallback(
    (planetId: number): Planet | undefined => {
      return gameState?.planets.find((p) => p.id === planetId);
    },
    [gameState]
  );

  const getFleetById = useCallback(
    (fleetId: number): Fleet | undefined => {
      return gameState?.fleets.find((f) => f.id === fleetId);
    },
    [gameState]
  );

  const getFleetsAtPlanet = useCallback(
    (planetId: number): Fleet[] => {
      return gameState?.fleets.filter((f) => f.current_planet_id === planetId) || [];
    },
    [gameState]
  );

  const getMyFleets = useCallback((): Fleet[] => {
    return gameState?.fleets.filter((f) => f.player_id === gameState.myPlayerId) || [];
  }, [gameState]);

  return {
    gameState,
    isLoading,
    error,
    selectedPlanetId,
    selectedFleetId,
    setSelectedPlanetId,
    setSelectedFleetId,
    refreshMap,
    getPlayerColor,
    getPlanetById,
    getFleetById,
    getFleetsAtPlanet,
    getMyFleets,
  };
}

export default useGameState;
