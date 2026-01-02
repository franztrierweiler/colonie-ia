/**
 * API Client for Colonie-IA backend
 */
import axios from 'axios';
import type { AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true,
    });

    // Request interceptor for auth token
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Try to refresh token
          const refreshed = await this.refreshToken();
          if (refreshed && error.config) {
            return this.client.request(error.config);
          }
        }
        return Promise.reject(error);
      }
    );
  }

  private async refreshToken(): Promise<boolean> {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) return false;

      const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
        refresh_token: refreshToken,
      });

      const { access_token } = response.data;
      localStorage.setItem('access_token', access_token);
      return true;
    } catch {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      return false;
    }
  }

  // Health check
  async health() {
    const response = await this.client.get('/health');
    return response.data;
  }

  // Version
  async version() {
    const response = await this.client.get('/version');
    return response.data;
  }

  // Auth endpoints (to be implemented in Phase 4)
  async login(email: string, password: string) {
    const response = await this.client.post('/auth/login', { email, password });
    const { access_token, refresh_token } = response.data;
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    return response.data;
  }

  async register(email: string, password: string, pseudo: string) {
    const response = await this.client.post('/auth/register', {
      email,
      password,
      pseudo,
    });
    return response.data;
  }

  async logout() {
    try {
      await this.client.post('/auth/logout');
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  }

  async getProfile() {
    const response = await this.client.get('/users/me');
    return response.data;
  }

  async updateProfile(data: { pseudo?: string; avatar_url?: string }) {
    const response = await this.client.patch('/users/me', data);
    return response.data;
  }

  async deleteAccount() {
    const response = await this.client.delete('/users/me');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    return response.data;
  }

  async checkGoogleOAuth(): Promise<boolean> {
    try {
      const response = await this.client.get('/auth/google/status');
      return response.data.enabled;
    } catch {
      return false;
    }
  }

  async forgotPassword(email: string) {
    const response = await this.client.post('/auth/forgot-password', { email });
    return response.data;
  }

  async resetPassword(token: string, password: string) {
    const response = await this.client.post('/auth/reset-password', { token, password });
    return response.data;
  }

  // Game endpoints

  async createGame(data: {
    name: string;
    galaxy_shape?: string;
    galaxy_size?: string;
    galaxy_density?: string;
    max_players?: number;
    turn_duration_years?: number;
    alliances_enabled?: boolean;
    combat_luck_enabled?: boolean;
  }) {
    const response = await this.client.post('/games', data);
    return response.data;
  }

  async listGames() {
    const response = await this.client.get('/games');
    return response.data;
  }

  async getGame(gameId: number) {
    const response = await this.client.get(`/games/${gameId}`);
    return response.data;
  }

  async deleteGame(gameId: number) {
    const response = await this.client.delete(`/games/${gameId}`);
    return response.data;
  }

  async joinGame(gameId: number) {
    const response = await this.client.post(`/games/${gameId}/join`);
    return response.data;
  }

  async leaveGame(gameId: number) {
    const response = await this.client.post(`/games/${gameId}/leave`);
    return response.data;
  }

  async addAIPlayer(gameId: number, difficulty: string = 'medium', name?: string) {
    const response = await this.client.post(`/games/${gameId}/ai`, { difficulty, name });
    return response.data;
  }

  async removeAIPlayer(gameId: number, playerId: number) {
    const response = await this.client.delete(`/games/${gameId}/ai/${playerId}`);
    return response.data;
  }

  async setPlayerReady(gameId: number, ready: boolean = true) {
    const response = await this.client.post(`/games/${gameId}/ready`, { ready });
    return response.data;
  }

  async startGame(gameId: number) {
    const response = await this.client.post(`/games/${gameId}/start`);
    return response.data;
  }

  async getMyGames() {
    const response = await this.client.get('/games/my');
    return response.data;
  }

  // Game map endpoint
  async getGameMap(gameId: number) {
    const response = await this.client.get(`/games/${gameId}/map`);
    return response.data;
  }

  // Economy endpoint
  async getEconomy(gameId: number) {
    const response = await this.client.get(`/games/${gameId}/economy`);
    return response.data;
  }

  // Planet endpoints
  async updatePlanetBudget(
    planetId: number,
    terraformBudget: number,
    miningBudget: number,
    shipsBudget: number
  ) {
    const response = await this.client.patch(`/planets/${planetId}/budget`, {
      terraform_budget: terraformBudget,
      mining_budget: miningBudget,
      ships_budget: shipsBudget,
    });
    return response.data;
  }

  // Production Queue endpoints
  async getProductionQueue(planetId: number) {
    const response = await this.client.get(`/planets/${planetId}/production`);
    return response.data;
  }

  async addToProductionQueue(
    planetId: number,
    designId: number,
    fleetId?: number,
    count: number = 1
  ) {
    const response = await this.client.post(`/planets/${planetId}/production`, {
      design_id: designId,
      fleet_id: fleetId,
      count,
    });
    return response.data;
  }

  async removeFromProductionQueue(queueId: number) {
    const response = await this.client.delete(`/production/${queueId}`);
    return response.data;
  }

  async abandonPlanet(planetId: number, stripMine: boolean = true) {
    const response = await this.client.post(`/planets/${planetId}/abandon`, {
      strip_mine: stripMine,
    });
    return response.data;
  }

  // ==========================================================================
  // Ship Design endpoints
  // ==========================================================================

  async getDesigns(gameId: number) {
    const response = await this.client.get(`/games/${gameId}/designs`);
    return response.data;
  }

  async createDesign(
    gameId: number,
    data: {
      name: string;
      ship_type: string;
      range_level?: number;
      speed_level?: number;
      weapons_level?: number;
      shields_level?: number;
      mini_level?: number;
    }
  ) {
    const response = await this.client.post(`/games/${gameId}/designs`, data);
    return response.data;
  }

  async getDesignCosts(gameId: number, designId: number) {
    const response = await this.client.get(`/games/${gameId}/designs/${designId}/costs`);
    return response.data;
  }

  async buildShips(gameId: number, designId: number, fleetId: number, count: number = 1) {
    const response = await this.client.post(`/games/${gameId}/designs/${designId}/build`, {
      fleet_id: fleetId,
      count,
    });
    return response.data;
  }

  // ==========================================================================
  // Fleet endpoints
  // ==========================================================================

  async getFleets(gameId: number) {
    const response = await this.client.get(`/games/${gameId}/fleets`);
    return response.data;
  }

  async getFleet(fleetId: number) {
    const response = await this.client.get(`/fleets/${fleetId}`);
    return response.data;
  }

  async createFleet(gameId: number, name: string, planetId?: number) {
    const response = await this.client.post(`/games/${gameId}/fleets`, {
      name,
      planet_id: planetId,
    });
    return response.data;
  }

  async moveFleet(fleetId: number, destinationPlanetId: number) {
    const response = await this.client.post(`/fleets/${fleetId}/move`, {
      destination_planet_id: destinationPlanetId,
    });
    return response.data;
  }

  async splitFleet(fleetId: number, shipIds: number[], newFleetName: string) {
    const response = await this.client.post(`/fleets/${fleetId}/split`, {
      ship_ids: shipIds,
      new_fleet_name: newFleetName,
    });
    return response.data;
  }

  async mergeFleets(fleetId: number, fleetIdToMerge: number) {
    const response = await this.client.post(`/fleets/${fleetId}/merge`, {
      fleet_id_to_merge: fleetIdToMerge,
    });
    return response.data;
  }

  async disbandFleet(fleetId: number) {
    const response = await this.client.post(`/fleets/${fleetId}/disband`);
    return response.data;
  }

  async disbandShip(shipId: number) {
    const response = await this.client.post(`/ships/${shipId}/disband`);
    return response.data;
  }
}

export const api = new ApiClient();
export default api;
