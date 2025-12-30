import { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

// Types
export interface Planet {
  id: number;
  name: string;
  star_id: number;
  orbit_index: number;
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
  is_home_planet: boolean;
}

export interface Star {
  id: number;
  name: string;
  x: number;
  y: number;
  is_nova: boolean;
  planet_count: number;
  planets: Planet[];
}

export interface Fleet {
  id: number;
  name: string;
  player_id: number;
  status: string;
  current_star_id: number | null;
  destination_star_id: number | null;
  departure_turn: number | null;
  arrival_turn: number | null;
  ship_count: number;
  fleet_speed: number;
  fleet_range: number;
  total_weapons: number;
  total_shields: number;
  ships_by_type: Record<string, number>;
}

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
  star_count: number;
}

export interface GameState {
  gameId: number;
  turn: number;
  myPlayerId: number;
  galaxy: Galaxy;
  stars: Star[];
  fleets: Fleet[];
  players: Player[];
}

interface UseGameStateReturn {
  gameState: GameState | null;
  isLoading: boolean;
  error: string | null;
  selectedStarId: number | null;
  selectedFleetId: number | null;
  setSelectedStarId: (id: number | null) => void;
  setSelectedFleetId: (id: number | null) => void;
  refreshMap: () => Promise<void>;
  getPlayerColor: (playerId: number | null) => string;
  getStarById: (starId: number) => Star | undefined;
  getFleetById: (fleetId: number) => Fleet | undefined;
  getFleetsAtStar: (starId: number) => Fleet[];
  getMyFleets: () => Fleet[];
}

export function useGameState(gameId: number | undefined): UseGameStateReturn {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedStarId, setSelectedStarId] = useState<number | null>(null);
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
        stars: data.stars,
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

  const getStarById = useCallback(
    (starId: number): Star | undefined => {
      return gameState?.stars.find((s) => s.id === starId);
    },
    [gameState]
  );

  const getFleetById = useCallback(
    (fleetId: number): Fleet | undefined => {
      return gameState?.fleets.find((f) => f.id === fleetId);
    },
    [gameState]
  );

  const getFleetsAtStar = useCallback(
    (starId: number): Fleet[] => {
      return gameState?.fleets.filter((f) => f.current_star_id === starId) || [];
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
    selectedStarId,
    selectedFleetId,
    setSelectedStarId,
    setSelectedFleetId,
    refreshMap,
    getPlayerColor,
    getStarById,
    getFleetById,
    getFleetsAtStar,
    getMyFleets,
  };
}

export default useGameState;
